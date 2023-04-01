import sys
import sysconfig
option=sys.argv[1]
if option == 'cxxflags':
 flags=sysconfig.get_config_var('CFLAGS').split()
 for unflag in ['-Wno-unused-result','-Wstrict-prototypes']:
  if flags.count(unflag) > 0:
   flags.remove(unflag)
 print(' '.join(flags))
elif option == 'headerdir':
 print(sysconfig.get_path('include'))
elif option == 'includes':
 print('-I' + sysconfig.get_path('include') + ' -I' + sysconfig.get_path('platinclude'))
elif option == 'ldflags':
 flags=sysconfig.get_config_var('LDFLAGS')
 if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
  flags+=' -L'+sysconfig.get_config_var('LIBPL')
 if not sysconfig.get_config_var('PYTHONFRAMEWORK'):
  flags+=' ' + sysconfig.get_config_var('LINKFORSHARED')
 print(flags)
elif option == 'libs':
 print('-lpython' + sysconfig.get_config_var('VERSION') + sys.abiflags + ' ' + sysconfig.get_config_var('LIBS') + ' ' + sysconfig.get_config_var('SYSLIBS'))
elif option == 'version':
 print(sysconfig.get_config_var('VERSION'))
