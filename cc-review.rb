#!/usr/bin/env ruby

require 'pp'
require 'xmlrpc/client'
require 'time'
require 'digest/md5'

CC_URI = URI.parse(`cat ~/.smartbear/com.smartbear.ccollab.client.txt | grep url=`.split('=')[1].chomp.gsub('\\',''))
SUPPORTED_SERVER_VERISON = 823
SVN_LOGIN = `cat ~/.subversion/auth/svn.simple/* | head -16 | tail -1`.chomp
SVN_PASSWORD = `cat ~/.subversion/auth/svn.simple/* | head -8 | tail -1`.chomp
CLIENT_GUID = `cat ~/.smartbear/com.smartbear.ccollab.client.txt | grep clientguid=`.split('=')[1].chomp
REPO_ROOT = `git svn info | grep "Repository Root:"`.split.last
REPO_UUID = `git svn info | grep "Repository UUID:"`.split.last
REPO_URL = `git svn info | grep "URL:"`.split.last
SVN_PREFIX = REPO_URL.sub(REPO_ROOT, '')
LOCAL_GUID = Digest::MD5.hexdigest(Time.now.to_f.to_s)

def find_files
  files = []
  puts "Files for review:"

  if ARGV.empty?
    `git diff-index #{@commit_hash}`.split("\n").each do |line|
      file_info = line.split
      files << { :action_type => file_info[4], :filename => file_info[5] }
      raise "Unsupported action type: #{file_info[4]}" if 'M' != file_info[4]
    end
  else
    ARGV.each { |file| files << { :action_type => 'M', :filename => file } }
  end

  raise "Files for review not found." if files.empty?

  files.each { |file| puts "  #{file[:action_type]}\t#{file[:filename]}"  }

  puts "Press Enter to continue..."
  STDIN.getc
  files
end

class XMLRPC::Client
  def set_debug
    @http.set_debug_output($stderr);
  end
end

puts "CodeCollaborator git-svn client."

begin
  if !ARGV.empty? && ARGV[0].to_i > 0
    review_id = ARGV.shift.to_i
  end

  @commit_hash = `git svn dcommit -n | tail -1`.split[1]
  @files = find_files

  @server = XMLRPC::Client.new(CC_URI.host, "/xmlrpc/server", CC_URI.port)
  @server.set_debug if 1 == ENV['CC_DEBUG']

  version = @server.call("ccollab3.getServerVersion")
  raise "Unknown server version #{version}" if SUPPORTED_SERVER_VERISON != version

  result = @server.call("ccollab.sessionAffirm", SVN_LOGIN, SVN_PASSWORD, { 'password-type' => 'plaintext', 'password-value' => SVN_PASSWORD })
  raise result['error']  if result.has_key?('error')

  review_id = @server.call("ccollab3.reviewCreate", SVN_LOGIN, 'Untitled') if !review_id

  result = @server.call("ccollab3.queryObjectsSimple", "com.smartbear.ccollab.datamodel.ScmData", {
    'configB' => REPO_UUID, 'configA' => REPO_ROOT, 'provider' => 'subversion'
  }, 1)
  scm_id = result.first['id'].to_i

  local_changelist_id = @server.call("ccollab3.changelistCreate", '', scm_id, LOCAL_GUID, Time.now, SVN_LOGIN, 'Local changes', CLIENT_GUID)

  @files.each do |file|
    puts "Uploading file #{file[:filename]}..."
    last_commit_info = `git svn log --limit 1 #{file[:filename]} | head -2 | tail -1`.chomp.split(" | ")
    commit_revision = last_commit_info[0].gsub(/[^\d]/, '\1')
    author = last_commit_info[1]
    time = Time.parse(last_commit_info[2])
    file_changelist_id = @server.call("ccollab3.changelistCreate", commit_revision, scm_id, '', time, author, 'fake comment', CLIENT_GUID)

    prev_version_id = @server.call("ccollab3.versionCreate", file_changelist_id, SVN_PREFIX + file[:filename], '', commit_revision, 'A', 'C')
    content = `git show #{@commit_hash}:#{file[:filename]}`
    content_md5 = Digest::MD5.hexdigest(content)
    @server.call("ccollab3.versionSetContentByMd5", prev_version_id, content_md5)
    @server.call("ccollab3.save", 'com.smartbear.ccollab.datamodel.VersionData', {
      'changelistId' => file_changelist_id, 'changeType' => 'A', 'prevVersionId' => 0, 'contentMd5' => content_md5,
      'id' => prev_version_id, 'scmVersionName' => commit_revision, 'localFilePath' => '', 'localType' => 'C',
      'filePath' => SVN_PREFIX + file[:filename]
    })

    commit_revision = `git svn info #{file[:filename]} | grep "Revision:"`.split.last
    version_id = @server.call("ccollab3.versionCreate", local_changelist_id, SVN_PREFIX + file[:filename],
      File.expand_path(file[:filename]), commit_revision, 'M', 'L'
    )
    @server.call("ccollab3.save", 'com.smartbear.ccollab.datamodel.VersionData', {
      'changelistId' => local_changelist_id, 'changeType' => 'M', 'prevVersionId' => prev_version_id, 'contentMd5' => '',
      'id' => version_id, 'scmVersionName' => commit_revision, 'localFilePath' => File.expand_path(file[:filename]), 'localType' => 'L',
      'filePath' => SVN_PREFIX + file[:filename]
    })
    content = `cat #{file[:filename]}`
    content_md5 = Digest::MD5.hexdigest(content)
    @server.call("ccollab3.versionSetContentByMd5", version_id, content_md5)
    @server.call("ccollab3.versionSetContent", version_id, XMLRPC::Base64.new(content))

    @server.call("ccollab3.save", 'com.smartbear.ccollab.datamodel.VersionData', {
      'changelistId' => local_changelist_id, 'changeType' => 'M', 'prevVersionId' => prev_version_id, 'contentMd5' => content_md5,
      'id' => version_id, 'scmVersionName' => commit_revision, 'localFilePath' => File.expand_path(file[:filename]), 'localType' => 'L',
      'filePath' => SVN_PREFIX + file[:filename]
    })
  end

  @server.call("ccollab3.reviewAddChangelist", review_id, local_changelist_id)

  puts "Review with id #{review_id} was created."
  puts "http://#{CC_URI.host}:#{CC_URI.port}/index.jsp?page=ReviewDisplay&reviewid=#{review_id}"
rescue Exception => e
  puts e.message
  exit 1
end
