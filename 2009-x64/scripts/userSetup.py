if not globals().get('_USER_SETUP_EXECUTED', False):
    _USER_SETUP_EXECUTED = True
    
    IMPORT_PYMEL = True
    VERBOSE = True
    ADDMAYAPATHS = True

    if VERBOSE:
        print "userSetup.py..."

    if VERBOSE:
        print "Trying to run startup.py..."
    import os, sys
    filename = os.environ.get('PYTHONSTARTUP')
    if filename and os.path.isfile(filename):
        execfile(filename)
        if VERBOSE:
            print "Finished startup.py..."
    else:
        print "Could not load PYTHONSTARTUP - '%s'" % filename
    from PMP.sysUtils import setDefaultEnvValue
    
    def addToPath(path):
        import PMP.sysUtils
        return PMP.sysUtils.addToPath(path, verbose=VERBOSE)
    
    import maya.cmds as cmds
    from maya.cmds import *
    # So that standard python builtins, like 'open', are preserved
    from __builtin__ import *
    import maya.mel as mel
    from maya.mel import eval as meval
    import maya.OpenMaya as api

    # If executed by a normal maya startup, __file__ will not be defined...
    # ...but in that case, cmds.internalVar(userScriptDir=1) should work
    try:
        _thisModuleDir = cmds.internalVar(userScriptDir=1)
    except:
        _thisModuleDir = os.path.dirname(__file__)
    _thisModuleDir = os.path.realpath(_thisModuleDir)

    eclipseProjects = (os.path.join('pymelProject', 'pymel'),
                       os.path.join('abxPickerProject', 'abxPicker'),
                       os.path.join('heatWeightProject', 'src'),
                       os.path.join('TempScripts', 'src'))
    # workspaces = (r"C:\Dev\Projects\eclipse\workspace",
    #               os.path.join(os.environ['USB_ROOT'], "HomeMirror", "iAudioApps", "eclipse", "workspace"))
    workspaces = [os.path.join(os.environ['PAUL_C_DRIVE'],
                               *("Dev/Projects/eclipse/workspace".split('/')))]
    workspaces = [workspace for workspace in workspaces if os.path.isdir(workspace)]
    for project in eclipseProjects:
        for projectDir in [os.path.join(workspace, project) for workspace in workspaces]:
            if os.path.isdir(projectDir):
                addToPath(projectDir)
                break
    
    # Note that using these functions ONLY works within userSetup.py, as
    # we are setting the versionedDir/appDir by assuming that userSetup.py is located at:
    # mayaAppDir/mayaVersionedAppDir/scripts/userSetup.py
    
    @setDefaultEnvValue('MAYA_VERSIONED_SETTINGS_DIR')
    def setMayaVersionedAppDir():
        return os.path.dirname(_thisModuleDir)
           
    @setDefaultEnvValue('MAYA_APP_DIR')
    def setMayaAppDir():
        return os.path.dirname(setMayaVersionedAppDir())
    
    @setDefaultEnvValue('MAYA_LOCATION')
    def setMayaLocation():
        for dir in (r"C:\3D\Maya2008", r"C:\Program Files\Autodesk\Maya2008"):
            if os.path.isdir(dir):
                return dir
    
    #@setDefaultEnvValue('PYMEL')
    #def setPymelLocation():
    #    return os.path.join(setMayaVersionedAppDir(), "PyMelBase")
    
    # Note also that we shouldn't need to call mayaVersionedAppDir in order to
    # set the env. var, as it is called by setMayaAppDir, but I'm doing it anyway, just
    # to be safe
    setMayaVersionedAppDir()
    setMayaAppDir()
    setMayaLocation()
    
    #addToPath(_thisModuleDir)
    
    if IMPORT_PYMEL:
        pymelImported = True
        if VERBOSE:
            print "Trying to import pymel..."
        try:
            from pymel.all import *
        except ImportError:
            try:
                from pymel import *
            except Exception:
                pymelImported = False
        except Exception:
            pymelImported = False
            
        if pymelImported:
            if VERBOSE:
                print "pymel successfully imported!"
            from pymel.util import refreshEnviron
            try:
                from tests.pymel_test import nose_test as pymel_test
            except Exception:
                print "failed to import pymel_test"
                if VERBOSE:
                    import traceback
                    traceback.print_exc()
        else:
            print "pymel import failed..."
            if VERBOSE:
                import traceback
                traceback.print_exc()
    
    if 'refreshEnviron' not in locals():
        import platform, subprocess
        
        if VERBOSE:
            print "refreshEnviron not loaded from pymel, defining..."
    
        def executableOutput(exeAndArgs, convertNewlines=True, stripTrailingNewline=True, **kwargs):
            """Will return the text output of running the given executable with the given arguments.
            
            This is just a convenience wrapper for subprocess.Popen, so the exeAndArgs argment
            should have the same format as the first argument to Popen: ie, either a single string
            giving the executable, or a list where the first element is the executable and the rest
            are arguments. 
            
            convertNewlines: if True, will replace os-specific newlines (ie, '\r\n' on Windows) with
                the standard '\n' newline
                
            stripTrailingNewline: if True, and the output from the executable contains a final newline,
                it is removed from the return value
                Note: the newline that is stripped is the one given by os.linesep, not '\n'
            
            kwargs are passed onto subprocess.Popen
            
            Note that if the keyword arg 'stdout' is supplied (and is something other than subprocess.PIPE),
            then the return will be empty - you must check the file object supplied as the stdout yourself.
            
            Also, 'stderr' is given the default value of subprocess.STDOUT, so that the return will be
            the combined output of stdout and stderr.
            
            Finally, since maya's python build doesn't support universal_newlines, this is always set to False - 
            however, set convertNewlines to True for an equivalent result."""
            
            kwargs.setdefault('stdout', subprocess.PIPE)
            kwargs.setdefault('stderr', subprocess.STDOUT)
            
            cmdProcess = subprocess.Popen(exeAndArgs, **kwargs)
            cmdOutput = cmdProcess.communicate()[0]
        
            if stripTrailingNewline and cmdOutput.endswith(os.linesep):
                cmdOutput = cmdOutput[:-len(os.linesep)]
        
            if convertNewlines:
                cmdOutput = cmdOutput.replace(os.linesep, '\n')
            return cmdOutput
        
        def shellOutput(shellCommand, convertNewlines=True, stripTrailingNewline=True, **kwargs):
            """Will return the text output of running a given shell command.
            
            convertNewlines: if True, will replace os-specific newlines (ie, '\r\n' on Windows) with
                the standard '\n' newline
                
            stripTrailingNewline: if True, and the output from the shell contains a final newline,
                it is removed from the return value
                Note: the newline that is stripped is the one given by os.linesep, not '\n'
            
            With default arguments, behaves like commands.getoutput(shellCommand),
            except it works on windows as well.
            
            kwargs are passed onto subprocess.Popen
            
            Note that if the keyword arg 'stdout' is supplied (and is something other than subprocess.PIPE),
            then the return will be empty - you must check the file object supplied as the stdout yourself.
            
            Also, 'stderr' is given the default value of subprocess.STDOUT, so that the return will be
            the combined output of stdout and stderr.
            
            Finally, since maya's python build doesn't support universal_newlines, this is always set to False - 
            however, set convertNewlines to True for an equivalent result."""
            
            # commands module not supported on windows... use subprocess
            kwargs['shell'] = True
            kwargs['convertNewlines'] = convertNewlines
            kwargs['stripTrailingNewline'] = stripTrailingNewline
            return executableOutput(shellCommand, **kwargs)
        
    
        def refreshEnviron():
            """
            copy the shell environment into python's environment, as stored in os.environ
            """ 
            exclude = ['SHLVL'] 
            
            if platform.system() in ('Darwin', 'Linux'):
                cmd = '/usr/bin/env'
            else:
                cmd = 'set'
                
            cmdOutput = shellOutput(cmd)
            #print "ENV", cmdOutput
            # use splitlines rather than split('\n') for better handling of different
            # newline characters on various os's
            for line in cmdOutput.splitlines():
                # need the check for '=' in line b/c on windows (and perhaps on other systems? orenouard?), an extra empty line may be appended
                if '=' in line:
                    var, val = line.split('=', 1)  # split at most once, so that lines such as 'smiley==)' will work
                    if not var.startswith('_') and var not in exclude: 
                            os.environ[var] = val 
    
    refreshEnviron()

    import PMP.mayaUtils
    import PMP.maya.fileUtils
    from PMP.maya import hw

    for path in (r"C:\Program Files\Autodesk\MayaBonusTools%d\python"  % PMP.mayaUtils.getMayaVersion(),
                 r"C:\MayaBonusTools%d\python" % PMP.mayaUtils.getMayaVersion(),
                 os.path.join(os.environ["OMTOOLBOX"], "pyScripts"),
                 os.path.join(os.environ["PAUL_SCRIPTS"], "pyScripts"),
                 os.path.join(os.environ["PAUL_C_DRIVE"],
                     *r"Dev\eclipse\plugins\org.python.pydev.debug_1.4.5.2727\pysrc".split('\\'))
                 ):
        try:
            addToPath(path)
        except Exception:
            print "Error adding %s to python path..." % path

    # Unfortunately, it seems the point at which userSetup.py is run is
    # too late to update MAYA_PLUG_IN_PATH

    # extraPluginDir = os.environ['MAYA_VERSIONED_SETTINGS_DIR']
    # if cmds.about(is64=True):
    #     extraPluginDir += 'plug-ins 64-bit'
    # else:
    #     extraPluginDir += 'plug-ins 32-bit'
    # os.environ['MAYA_PLUG_IN_PATH'] = os.environ['MAYA_PLUG_IN_PATH'] + os.pathsep + extraPluginDir

    PMP.maya.fileUtils.addProjectToPythonPath()
    workspaceChangedScriptJob = cmds.scriptJob(event=["workspaceChanged",
        "import PMP.maya.fileUtils;PMP.maya.fileUtils.addProjectToPythonPath()"
        ])
    PMP.maya.fileUtils.openLastProject(verbose=VERBOSE)

    #####################################################
    
    #for path in sys.path:
    #    if "pymel" in path.lower():
            
    
    # Old interactive console setup:
    
    #import os, os.path, platform
    #
    ##os.environ['MAYA_APP_DIR'] = os.path.join(os.environ['USERPROFILE'], 'My Documents', 'maya')
    #
    #if(os.environ['USERNAME'] == "Elrond"):
    #    os.environ['MAYA_LOCATION'] =  r"C:\3D\Maya2008"
    #    #paulLocation = "home"
    #else:
    #    os.environ['MAYA_LOCATION'] = r"C:\Program Files\Autodesk\Maya2008"
    #    #paulLocation = "expression"
    #
    ##import maya.standalone
    ##maya.standalone.initialize('eclipse')
    ##import pymel
    #
    #versionName = '2008'
    #if platform.system() in ('Microsoft', 'Windows') and (os.environ['PROCESSOR_ARCHITECTURE'] == 'AMD64'):
    #    versionName += '-x64'
    #
    ##sys.path.append(os.path.join(os.environ['MAYA_APP_DIR'], versionName, 'scripts'))
    #
    ##from userSetup import *

    if VERBOSE:
        print "...userSetup.py finished!!"
