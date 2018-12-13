Name:           LuaJIT
Version:        2.0.5
Release:        1%{?dist}
Summary:        LuaJIT

Group:          Development/Languages
License:        MIT
URL:            http://luajit.org/
Source0:        http://luajit.org/download/LuaJIT-2.0.5.tar.gz

BuildRequires:  gcc

%description
LuaJIT 2.0.5, rpm packaged by james@ustc.edu.cn 20181210

%prep
%setup -q
sed -i -e 's/export PREFIX= \/usr\/local/export PREFIX= \/usr/' Makefile

%build
%define debug_package %{nil}
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
cp src/luajit $RPM_BUILD_ROOT/%{_bindir}

mkdir -p $RPM_BUILD_ROOT/%{_includedir}/luajit-2.0
cp src/lua.h src/lualib.h src/luajit.h src/lauxlib.h src/lua.hpp src/luaconf.h $RPM_BUILD_ROOT/%{_includedir}/luajit-2.0

mkdir -p $RPM_BUILD_ROOT/%{_libdir}
cp src/libluajit.a $RPM_BUILD_ROOT/%{_libdir}/libluajit-5.1.a
cp src/libluajit.so $RPM_BUILD_ROOT/%{_libdir}/libluajit-5.1.so.2.0.5
ln -s libluajit-5.1.so.2.0.5 $RPM_BUILD_ROOT/%{_libdir}/libluajit-5.1.so
ln -s libluajit-5.1.so.2.0.5 $RPM_BUILD_ROOT/%{_libdir}/libluajit-5.1.so.2

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/luajit-2.0.5/jit/
cp src/jit/* $RPM_BUILD_ROOT/%{_datadir}/luajit-2.0.5/jit/

mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man1
cp etc/luajit.1 $RPM_BUILD_ROOT/%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/luajit
%{_includedir}/luajit-2.0/*
%{_libdir}/*
%{_datadir}/luajit-2.0.5/jit/*
%{_mandir}/man1/*

%doc

%changelog
