#!/usr/bin/env bats

@test "pacco remote list" {
  result="$(pacco remote list)"
  [ "${result}" == "[]" ]
}

@test "pacco remote add" {
  echo 'local_remote_path' | pacco remote add local_remote local
  result="$(pacco remote list)"
  [ "${result}" == "['local_remote']" ]
  pacco remote remove local_remote
  rm -rf local_remote_path
}

@test "pacco remote remove" {
  echo 'local_remote_path' | pacco remote add local_remote local
  pacco remote remove local_remote
  result="$(pacco remote list)"
  [ "${result}" == "[]" ]
  rm -rf local_remote_path
}

@test "pacco remote list_default" {
  result="$(pacco remote list_default)"
  [ "${result}" == "[]" ]
}

@test "pacco remote set_default" {
  echo 'local_remote_path' | pacco remote add local_remote local
  pacco remote set_default local_remote
  result="$(pacco remote list_default)"
  [ "${result}" == "['local_remote']" ]
  pacco remote set_default
  pacco remote remove local_remote
  rm -rf local_remote_path
}

@test "pacco registry list" {
  echo 'local_remote_path' | pacco remote add local_remote local
  result="$(pacco registry list local_remote)"
  [ "${result}" == "[]" ]
  pacco remote remove local_remote
  rm -rf local_remote_path
}

@test "pacco registry add" {
  echo 'local_remote_path' | pacco remote add local_remote local
  pacco registry add local_remote openssl os,version,obfuscation
  result="$(pacco registry list local_remote)"
  [ "${result}" == "['openssl']" ]
  pacco registry remove local_remote openssl
  pacco remote remove local_remote
  rm -rf local_remote_path
}

@test "pacco registry remove" {
  echo 'local_remote_path' | pacco remote add local_remote local
  pacco registry add local_remote openssl os,version,obfuscation
  pacco registry remove local_remote openssl
  result="$(pacco registry list local_remote)"
  [ "${result}" == "[]" ]
  pacco remote remove local_remote
  rm -rf local_remote_path
}

@test "pacco registry binaries" {
  echo 'local_remote_path' | pacco remote add local_remote local
  pacco registry add local_remote openssl os,version,obfuscation
  result="$(pacco registry binaries local_remote openssl)"
  [ "${result}" == "[]" ]
  pacco registry remove local_remote openssl
  pacco remote remove local_remote
  rm -rf local_remote_path
}

@test "pacco binary upload" {
  echo 'local_remote_path' | pacco remote add local_remote local
  pacco registry add local_remote openssl os,version,obfuscation
  mkdir openssl_upload_dir && touch openssl_upload_dir/sample.a
  pacco binary upload local_remote openssl openssl_upload_dir os=android,version=2.1.0,obfuscation=obfuscated
  result="$(pacco registry binaries local_remote openssl)"
  [ "${result}" == "[{'obfuscation': 'obfuscated', 'os': 'android', 'version': '2.1.0'}]" ]
  pacco binary remove local_remote openssl os=android,version=2.1.0,obfuscation=obfuscated
  rm -rf openssl_upload_dir
  pacco registry remove local_remote openssl
  pacco remote remove local_remote
  rm -rf local_remote_path
}

@test "pacco binary download" {
  echo 'local_remote_path' | pacco remote add local_remote local
  pacco registry add local_remote openssl os,version,obfuscation
  mkdir openssl_upload_dir && touch openssl_upload_dir/sample.a
  pacco binary upload local_remote openssl openssl_upload_dir os=android,version=2.1.0,obfuscation=obfuscated
  pacco binary download local_remote openssl openssl_download_dir os=android,version=2.1.0,obfuscation=obfuscated
  result="$(ls openssl_download_dir)"
  [ "${result}" == "sample.a" ]
  pacco binary remove local_remote openssl os=android,version=2.1.0,obfuscation=obfuscated
  rm -rf openssl_download_dir openssl_upload_dir
  pacco registry remove local_remote openssl
  pacco remote remove local_remote
  rm -rf local_remote_path
}

@test "pacco binary remove" {
  echo 'local_remote_path' | pacco remote add local_remote local
  pacco registry add local_remote openssl os,version,obfuscation
  mkdir openssl_upload_dir && touch openssl_upload_dir/sample.a
  pacco binary upload local_remote openssl openssl_upload_dir os=android,version=2.1.0,obfuscation=obfuscated
  pacco binary remove local_remote openssl os=android,version=2.1.0,obfuscation=obfuscated
  result="$(pacco registry binaries local_remote openssl)"
  [ "${result}" == "[]" ]
  rm -rf openssl_upload_dir
  pacco registry remove local_remote openssl
  pacco remote remove local_remote
  rm -rf local_remote_path
}