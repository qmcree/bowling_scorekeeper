Vagrant.configure(2) do |config|
  config.vm.box = "nrel/CentOS-6.5-x86_64"
  config.vm.network "forwarded_port", guest: 8000, host: 4567
  config.vm.network "forwarded_port", guest: 5432, host: 5433
  config.vm.host_name = "challenges.dev"
end