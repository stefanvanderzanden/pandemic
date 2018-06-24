# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = 'hfm/centos7'

  config.vm.synced_folder "./pandemic", "/home/vagrant/pandemic/", create: true, owner: "vagrant", group: "vagrant"
  config.vm.network "forwarded_port", guest: 8000, host: 21000

  # Define RAM and CPU limitations for Virtualbox
  config.vm.provider :virtualbox do |vb|
      # Don't boot with headless mode
      # vb.gui = true

      # Use VBoxManage to customize the VM. For example to change memory:
      vb.memory = 2048
      vb.cpus = 1
  end

  #Start Ansible Provisioning
  config.vm.provision "ansible" do |ansible|
     ansible.playbook = "ansible/main.yml"
  end
end
