#
# spec file for package docbook-xsl-stylesheets
#
# Copyright (c) 2012 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%define pack_vers 1.77.1
%define regcat /usr/bin/sgml-register-catalog

Name:           docbook-xsl-stylesheets
Version:        1.77.1
Release:        0
License:        MPL-1.1 and MIT
Summary:        XSL Stylesheets for DocBook 4
Url:            http://sourceforge.net/projects/docbook/
Group:          Productivity/Publishing/DocBook
Source0:        http://switch.dl.sourceforge.net/sourceforge/docbook/docbook-xsl-%{pack_vers}.tar.bz2
Source1:        http://switch.dl.sourceforge.net/sourceforge/docbook/docbook-xsl-doc-%{version}.tar.bz2
Patch0:         %{name}-dbtoepub.patch
BuildRequires:  fdupes
BuildRequires:  sgml-skel
BuildRequires:  unzip
Requires(pre):  %{regcat}
Requires(pre):  /usr/bin/xmlcatalog
Requires(pre):  sgml-skel
Requires:       docbook_4
Requires:       xmlcharent
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%description
These are the XSL stylesheets for DocBook XML and "Simplified" DocBook
DTDs. Use these stylesheets for documents based on DocBook 4 and
earlier; they are not aware of the namespace feature.

The stylesheets transform DocBook documents into HTML, XHTML, Manpages,
XSL-FO (for PDF), and a few other formats.

XSL is a standard W3C stylesheet language for both print and online
rendering. For more information about XSL, see the XSL page at the W3C:
http://www.w3.org/Style/XSL/

%define INSTALL install -m755 -s
%define INSTALL_DIR install -d -m755
%define INSTALL_DATA install -m644
%define INSTALL_SCRIPT install -m755
%define sgml_dir %{_datadir}/sgml
%define sgml_var_dir /var/lib/sgml
%define sgml_mod_dir %{sgml_dir}/docbook
%define sgml_mod_dtd_dir %{sgml_mod_dir}/dtd
%define sgml_mod_custom_dir %{sgml_mod_dir}/custom
%define sgml_mod_style_dir %{sgml_mod_dir}/stylesheet
%define xml_dir %{_datadir}/xml
%define xml_mod_dir %{xml_dir}/docbook
%define xml_mod_dtd_dir %{xml_mod_dir}/dtd
%define xml_mod_custom_dir %{xml_mod_dir}/custom
%define xml_mod_style_dir %{xml_mod_dir}/stylesheet
%define xml_mod_style_prod_dir %{xml_mod_style_dir}/nwalsh
%define sgml_config_dir /var/lib/sgml
%define sgml_sysconf_dir %{_sysconfdir}/sgml
%define xml_config_dir /var/lib/xml
%define xml_sysconf_dir %{_sysconfdir}/xml

%prep
# %%setup -q -n docbook-xsl-%%{pack_vers} -b 10
%setup -q -n docbook-xsl-%{pack_vers} -b 1
%patch0 -p1

# mv epub/bin/dbtoepub epub/bin/dbtoepub.tmp
sed -i 's=@@EPUBDIR@@=%{xml_mod_style_prod_dir}/current//epub/bin='  epub/bin/dbtoepub

# We don't need these scripts:
rm -rf install.sh tools/bin/docbook-xsl-update

find -type f  -exec chmod -x {} \;
chmod -R a+rX,g-w,o-w .
chmod -x images/*.{svg,png,gif,tif} images/callouts/*.{svg,png,gif} extensions/docbook.py
# Start cleanup (to avoid warnings for rpmlint
[ -f ./extensions/saxon65/dist/saxon65.jar ] && rm -rf ./extensions/saxon65/dist/saxon65.jar
[ -f ./extensions/xalan27/dist/xalan27.jar ] && rm -rf ./extensions/xalan27/dist/xalan27.jar
find . -name '.gitignore' | xargs rm -fr
#x=$(find {lib,html,fo,lib,website,slides/fo,slides/html,roundtrip,manpages}/.[a-zA-Z0-9]* -maxdepth 1 -type f )
#if [ "$x" != '' ]; then
## rm $x;
#  for i in $x; do
#     if [ -f $i ]; then
#        rm $i
#     fi
#  done
#fi

%build
xmlcatbin=/usr/bin/xmlcatalog
CATALOG=%{name}.xml
# file:///usr/share/sgml/docbook/ = %%{sgml_mod_dir} map it to
# %%{xml_mod_style_prod_dir}/%%{version}
$xmlcatbin --noout --create $CATALOG
/usr/bin/xmlcatalog --noout --add "rewriteSystem" \
 "http://docbook.sourceforge.net/release/xsl/%{version}" \
 "file://%{xml_mod_style_prod_dir}/%{version}" $CATALOG
/usr/bin/xmlcatalog --noout --add "rewriteURI" \
 "http://docbook.sourceforge.net/release/xsl/%{version}" \
 "file://%{xml_mod_style_prod_dir}/%{version}" $CATALOG
/usr/bin/xmlcatalog --noout --add "rewriteSystem" \
 "http://docbook.sourceforge.net/release/xsl/current" \
 "file://%{xml_mod_style_prod_dir}/%{version}" $CATALOG
/usr/bin/xmlcatalog --noout --add "rewriteURI" \
 "http://docbook.sourceforge.net/release/xsl/current" \
 "file://%{xml_mod_style_prod_dir}/%{version}" $CATALOG
%define FOR_ROOT_CAT for-catalog-%{name}-%{version}.xml
CATALOG=etc/xml/$CATALOG
rm -f %{FOR_ROOT_CAT}.tmp
$xmlcatbin --noout --create %{FOR_ROOT_CAT}.tmp
$xmlcatbin --noout --add "delegateSystem" \
  "http://docbook.sourceforge.net/release/xsl/" \
  "file:///$CATALOG" %{FOR_ROOT_CAT}.tmp
# $xmlcatbin --noout --add "delegatePublic" \
#   "-//OASIS//xxx" \
#   "file:///$CATALOG" %%{FOR_ROOT_CAT}.tmp
# Create tag
sed '/<catalog/a\
  <group id="%{name}-%{version}">
/<\/catalog/i\
  </group>' \
  %{FOR_ROOT_CAT}.tmp > %{FOR_ROOT_CAT}

%install
# FIXME: Danger!?
# export NO_BRP_CHECK_BYTECODE_VERSION=true

# Install scripts
%{INSTALL_DIR} %{buildroot}%{_bindir}
%{INSTALL_SCRIPT} fo/pdf2index       %{buildroot}%{_bindir}
%{INSTALL_SCRIPT} epub/bin/dbtoepub  %{buildroot}%{_bindir}
rm fo/pdf2index

doc_dir=%{buildroot}%{_defaultdocdir}/%{name}
%{INSTALL_DIR} %{buildroot}%{xml_mod_style_prod_dir}/%{version}
cp -a [[:lower:]]* %{buildroot}%{xml_mod_style_prod_dir}/%{version}
cp -a VERSION.xsl %{buildroot}%{xml_mod_style_prod_dir}/%{version}
find %{buildroot}%{xml_mod_style_prod_dir} -type f -name '*.orig' -exec rm -f {} \;
rm -f %{buildroot}%{xml_mod_style_prod_dir}/%{version}/for-catalog*
: >%{name}_list
{
  pushd %{buildroot}%{xml_mod_style_prod_dir} >/dev/null
# do not create the current link for snapshots
#  if ! echo %%{SOURCE0} | grep -q snapshot; then
    ln -sf %{version} current
    echo %{xml_mod_style_prod_dir}/current
#  fi
  popd >/dev/null
} >%{name}_list
%{INSTALL_DIR} $doc_dir
# documentation
for f in README BUGS TODO WhatsNew RELEASE-NOTES.html; do
  # On snapshots, WhatsNew is missing
  [ -f $f ] && %{INSTALL_DATA} $f $doc_dir/$f
done
# cp -p README.SuSE $doc_dir/README.SuSE
#
{
  LANG=C \
    find %{buildroot}%{xml_mod_style_prod_dir}/%{version} \
    -type d \
    -not -path '%{buildroot}%{xml_mod_style_prod_dir}/%{version}/latex*' \
    | sed 's|%{buildroot}|%dir |'
  LANG=C \
    find %{buildroot}%{xml_mod_style_prod_dir}/%{version} \
    -type f \
    -not -path '%{buildroot}%{xml_mod_style_prod_dir}/%{version}/latex*' \
    | sed 's|%{buildroot}||'
} >> %{_builddir}/%{buildsubdir}/%{name}_list
# pushd %%{buildroot}%%{xml_mod_style_prod_dir}
#   rm -f docbook-xsl
#   ln -sf docbook-xsl-stylesheets-%%{version} docbook-xsl
#   rm -f xsl-stylesheets
#   ln -sf docbook-xsl-stylesheets-%%{version} xsl-stylesheets
#   rm -f %%{name}
#   ln -sf docbook-xsl-stylesheets-%%{version} %%{name}
# popd
cat_dir=%{buildroot}%{_sysconfdir}/xml
%{INSTALL_DIR} $cat_dir
%{INSTALL_DATA} %{FOR_ROOT_CAT} %{name}.xml $cat_dir
# cleanup
rm -f %{buildroot}%{xml_mod_style_prod_dir}/%{version}/%{name}.xml
cp $cat_dir/%{FOR_ROOT_CAT} \
  %{buildroot}%{xml_mod_style_prod_dir}/%{version}/%{name}.xml
chmod +x \
%{buildroot}%{xml_mod_style_prod_dir}/%{version}/extensions/docbook.py \
%{buildroot}%{xml_mod_style_prod_dir}/%{version}/extensions/xslt.py
# %%{buildroot}%%{xml_mod_style_prod_dir}/%%{version}/epub/bin/lib/docbook.rb
# %%{buildroot}%%{xml_mod_style_prod_dir}/%%{version}/epub/bin/spec/spec_helper.rb

%fdupes -s %{buildroot}


%post
# remove empty dir if present (from ghost)
# also remove dangling symlink
D=usr/share/sgml
rmdir $D/docbkxsl >/dev/null 2>&1 || :
test -L $D/docbkxsl -a ! -e $D/docbkxsl && rm -f $D/docbkxsl
if [ -x /usr/bin/edit-xml-catalog ]; then
  edit-xml-catalog --group --catalog /etc/xml/suse-catalog.xml \
    --add /etc/xml/%{FOR_ROOT_CAT}
fi

%postun
# remove entries only on removal of file
if [ ! -f %{xml_sysconf_dir}/%{FOR_ROOT_CAT} -a -x /usr/bin/edit-xml-catalog ] ; then
  edit-xml-catalog --group --catalog /etc/xml/suse-catalog.xml \
    --del %{name}-%{version}
fi

%files -f %{name}_list
%defattr(-, root, root)
%config %{_sysconfdir}/xml/%{name}.xml
%config %{_sysconfdir}/xml/%{FOR_ROOT_CAT}
%{_defaultdocdir}/%{name}
%dir %{xml_mod_style_dir}
%dir %{xml_mod_style_prod_dir}
# it is now in the list:
# %%{xml_mod_style_prod_dir}/current
%{_bindir}/*

%changelog
