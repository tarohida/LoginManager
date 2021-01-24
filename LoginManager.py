#!/usr/bin/python
#!coding:utf-8

import yaml
import json
import argparse
import subprocess


def import_yml(file_path):
  with open( file_path, 'r') as f:
    login_data_list = yaml.load( f )
  
  return login_data_list

def outport_yml(file_path, login_data_list):
  with open( file_path, 'w' ) as f:
    yaml.dump(login_data_list, f, default_flow_style=False)


class LoginManager:

  def __init__(self, template, ssh_config_path, login_data_file_path ):
    self.template = template
    self.ssh_config_path = ssh_config_path
    self.login_data_file_path = login_data_file_path

  def ssh_login(self, login_data):
    print(login_data)
    if not login_data['value']['password']:
      login_data['value']['password'] = 'none'
    print('password: ' + login_data['value']['password']) 
    if not login_data['value']['passphrase']:
      login_data['value']['passphrase'] = 'none'
    print('passphrase: ' + login_data['value']['passphrase'])
    subprocess.call(["ssh", login_data["host_id"]])
  
  def sync_ssh_config(self,login_data_list):
    line = '' 
    for login_data in login_data_list:
      if not login_data['login_method'] == 'ssh':
        continue
      line += 'Host ' + login_data['host_id'] + '\n'
      line += 'HostName ' + login_data['value']['ip_fqdn'] + '\n'
      line += 'User ' + login_data['value']['login_name'] + '\n'
      line += 'Port ' + login_data['value']['port'] + '\n'
      if login_data['value']['IdentityFile']:
        line += 'IdentityFile ' + login_data['value']['IdentityFile'] + '\n'
      line += '\n'
  
    with open( self.ssh_config_path , 'w') as f:
      f.write(line.encode('utf-8'))
  
    return True
  
  def telnet_login(self,login_data):
          print(login_data)
  
  def remote_desktop_login(self,login_data):
          print(login_data)
  
  def browser_login(self,login_data):
          print(login_data)
  
  def return_login_data(self,host_id, login_data_list):
          rtv = []
  
          for data in login_data_list:
                  if data['host_id'] == host_id:
                          return data
          
          return False 
  
  def registe_login_data(self,host_id, login_data_list, login_type=None):
    if not login_type:
      login_type = raw_input('please input type of login [ssh, remote_desktop, telnet, browser]--> ')

    def check_type(login_type):
      if login_type in template:
        return True
      else:
        return False

    if not check_type(login_type):
      raise Exception('script error: invalid type')

    tpl_copy = self.template[login_type].copy()
    need_values = self.template['need_values'][login_type]
    get_dict = {}
    for val in need_values:
      got_val = raw_input(val + ' --> ')
      dic = { val : got_val } 
      get_dict.update(dic)
    
    print(json.dumps(get_dict))
    for k,v in get_dict.items():
      if k in tpl_copy['value']:
        tpl_copy['value'][k] = v

    tpl_copy.update({'host_id': host_id})
  
    login_data_list.append(tpl_copy)
    print(login_data_list)
    outport_yml(self.login_data_file_path, login_data_list)
  
    self.sync_ssh_config(login_data_list)
  
    return True
  
  def login(self,host_id, login_data_list):
          login_data = self.return_login_data(host_id, login_data_list)
  
          if login_data:
            if login_data['banner']:
              print(login_data['banner'].encode('utf-8'))
  
            if login_data['login_method'] == 'ssh':
              self.ssh_login(login_data)
            elif login_data['login_method'] == 'telnet':
              self.telnet_login(login_data)
            elif login_data['login_method'] == 'remote_desktop':
              self.remote_desktop_login(login_data)
            elif login_data['login_method'] == 'browser':
              self.browser_login(login_data)
              pass
            else:
              raise Exception('script error: invalid type')
          else:
            self.registe_login_data(host_id, login_data_list)


if __name__ == '__main__':

  #argument------
  parser = argparse.ArgumentParser()
  parser.add_argument('host_id', help='imput host id')
  parser.add_argument('-m', '--modules', help='when use as module, use this option')
  arguments = parser.parse_args()
    #registe host_id
  host_id = arguments.host_id
  #-------

  #main----
  login_data_file_path = ""
  template_file_path = ""
  ssh_config_path = "" 

  login_data_list = import_yml(login_data_file_path)
  template = import_yml(template_file_path)
    #acceess like this -> template['ssh'], template['remote_desktop'], etc...

  if arguments.modules:
    if arguments.modules == 'sync':
      sync_ssh_config(login_data_list)
      exit()
    if arguments.modules == 'dump':
      print(json.dumps(login_data_list, indent=2))
      exit()

  login_manager = LoginManager(
    template,
    ssh_config_path,
    login_data_file_path
    )
  login_manager.login(host_id, login_data_list)
