from distutils.core import setup
setup(name='recce7',
      version='1.0',
      description='Report Server',
      author='Jesse Nelson',
      author_email='jnels124@msudenver.edu',
      data_files=[('/etc/recce7/configs/', ['install/configs/plugins.cfg', 'install/configs/global.cfg']),
                  ('/usr/sbin/recce7/database/sql_scripts', ['database/sql_scripts/sessions.sql',
                                                             'database/sql_scripts/p0f.sql',
                                                             'database/sql_scripts/ipInfo.sql']),
                  ('/etc/init.d/', ['install/scripts/recce7'])],
      scripts=['install/scripts/startReportServer.sh'],
      packages=['framework', 'plugins', 'database', 'common', 'recon', 'reportserver',
                'reportserver.dao', 'reportserver.manager', 'reportserver.server'])
