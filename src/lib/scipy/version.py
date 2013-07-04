# THIS FILE IS GENERATED FROM SCIPY SETUP.PY
short_version='0.9.0'
version='0.9.0'
release=True

if not release:
    version += '.dev'
    import os
    svn_version_file = os.path.join(os.path.dirname(__file__),
                                    '__svn_version__.py')
    if os.path.isfile(svn_version_file):
        import imp
        svn = imp.load_module('scipy.__svn_version__',
                              open(svn_version_file),
                              svn_version_file,
                              ('.py','U',1))
        version += svn.version
