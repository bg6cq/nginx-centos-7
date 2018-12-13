# CentOS 7 nginx编译和优化

CentOS本身没有nginx，epel中的nginx版本比较低，这里给出CentOS 7.6 编译nginx.1.42.2并包含lua支持的步骤，最后还给出一些系统优化的方法。

如果仅仅为了使用最新的nginx，不愿意自己编译，请下载CentOS 7.6 x86_64最小安装，
执行`rpm -i https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm`启用epep库，
按照"7. 使用远程 yum 源"，设置科大的nginx源，执行`yum update nginx`即可。这样安装的系统占用1G左右的磁盘空间。

注：run.sh 文件有完整的编译过程脚本，直接运行即可在全新安装的CentOS 7.6 中完成编译过程。

## 1. 环境准备

下载 CentOS 7.6 x86_64 最小安装

运行如下命令，启用epel库（geoip等在epel库中），安装rpmbuild等需要的软件包

```
rpm -i https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum -y install git gcc rpm-build rpmdevtools geoip-devel gd-devel pcre-devel
yum -y install perl-devel perl-ExtUtils-Embed libxslt-devel gperftools-devel createrepo
yum -y update
reboot
```

## 2. 下载编译需要的文件

编译需要的文件放在 https://git.ustc.edu.cn/james/nginx-centos-7 ，下载到默认的`/root/rpmbuild`目录

下载前该目录不能存在。如果目录已经存在，请下载到其他位置，把SOURCES、SPECS目录下文件 copy 到`/root/rpmbuild`对应目录下也可以。

```
cd /root
git clone https://git.ustc.edu.cn/james/nginx-centos-7.git rpmbuild
```

## 3. 编译需要的LuaJIT，并安装

编译好的文件在`/root/rpmbuild/RPMS/x86_64`目录。

```
cd /root/rpmbuild
rpmbuild -bb SPECS/LuaJIT.spec

rpm -i RPMS/x86_64/LuaJIT-2.0.5-1.el6.x86_64.rpm
```

## 4. 编译nginx

```
cd /root/rpmbuild
rpmbuild -ba SPECS/nginx.spec
```
编译好的文件在`/root/rpmbuild/RPMS/x86_64`和`/root/rpmbuild/RPMS/noarch`目录。

## 5. 搭建yum库

编译好的rpm包可以安装，但是自己手工安装需要处理依赖关系，比较麻烦。

下面是搭建yum库的方法。

```
mkdir -p /var/www/html/local-yum/7/x86_64/RPMS
cp /root/rpmbuild/RPMS/x86_64/* /root/rpmbuild/RPMS/noarch/* /var/www/html/local-yum/7/x86_64/RPMS
createrepo /var/www/html/local-yum/7/x86_64/
```

## 6. 使用本地yum源

如果是本地使用，建立文件`/etc/yum.repos.d/local.repo`，内容为：
```
[local-yum]
name=local-yum
baseurl=file:///var/www/html/local-yum/7/x86_64
enabled=1
gpgcheck=0
```
之后就可以使用自己本地源。

## 7. 使用远程 yum 源

如果把`/var/www/html/local-yum/`目录通过web服务器对外提供，其他机器只要 建立文件`/etc/yum.repos.d/local.repo`即可使用。
```
[local-yum]
name=local-yum
baseurl=http://revproxy.ustc.edu.cn:8000/local-yum/7/x86_64
enabled=1
gpgcheck=0
```

## 8. 系统优化

8.1 禁用SELINUX

编辑文件`/etc/selinux/config`，把`SELINUX=enforcing`修改为`SELINUX=disabled`

8.2 增加打开的文件数

编辑文件`vi /etc/security/limits.conf`，增加4行：
```
*               soft    nofile  655360
*               hard    nofile  655360
root            soft    nofile  655360
root            hard    nofile  655360
```

编辑文件`vi /etc/sysctl.d/file-max.conf`，增加1行:
```
fs.file-max = 655360
```

8.3 优化nf_conntrack部分

编辑文件`/etc/modprobe.d/firewalld-sysctls.conf`，增加hashsize=13107即可把最大连接数修改为104万。
```
install nf_conntrack /usr/sbin/modprobe --ignore-install nf_conntrack hashsize=131072 $CMDLINE_OPTS && /usr/sbin/sysctl --quiet --pattern 'net[.]netfilter[.]nf_conntrack.*' --sys
tem
```

启动过程中，增加如下代码，减少conntrack超时时间：
```
cd /proc/sys/net/netfilter
echo 60 > nf_conntrack_generic_timeout
echo 10 > nf_conntrack_icmp_timeout
echo 10 > nf_conntrack_icmpv6_timeout
echo 10 > nf_conntrack_tcp_timeout_close
echo 10 > nf_conntrack_tcp_timeout_last_ack
echo 10 > nf_conntrack_tcp_timeout_time_wait
echo 10 > nf_conntrack_tcp_timeout_close_wait
echo 10 > nf_conntrack_tcp_timeout_max_retrans
echo 10 > nf_conntrack_tcp_timeout_unacknowledged
echo 600 > nf_conntrack_tcp_timeout_established
echo 60 > nf_conntrack_tcp_timeout_syn_recv
echo 10 > nf_conntrack_tcp_timeout_fin_wait
echo 30 > nf_conntrack_tcp_timeout_syn_sent
echo 10 > nf_conntrack_udp_timeout
echo 60 > nf_conntrack_udp_timeout_stream
echo 60 > nf_conntrack_dccp_timeout_open
echo 60 > nf_conntrack_dccp_timeout_partopen
echo 60 > nf_conntrack_dccp_timeout_request
echo 60 > nf_conntrack_dccp_timeout_respond
echo 60 > nf_conntrack_dccp_timeout_timewait
echo 600 > nf_conntrack_sctp_timeout_established
```

## 附录：

CentOS epel 默认的nginx之外，下载了如下软件：

* http://nginx.org/download/nginx-1.14.2.tar.gz http://nginx.org/download/nginx-1.14.2.tar.gz.asc
* http://luajit.org/download/LuaJIT-2.0.5.tar.gz
* https://www.openssl.org/source/openssl-1.1.1a.tar.gz
* https://github.com/simplresty/ngx_devel_kit/archive/v0.3.0.tar.gz
* https://github.com/openresty/lua-nginx-module/archive/v0.10.13.tar.gz
