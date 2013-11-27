#include "cube.h"

#define PY_ERR(x) \
	if(!x) \
	{ \
		if(PyErr_Occurred()) \
			PyErr_Print(); \
			return false; \
	}

PyMODINIT_FUNC initModule();

bool initCore() {
    PyObject *pFunc = 0, *pArgs = 0, *pValue = 0, *pluginsModule = 0;
    logline(ACLOG_INFO,":  Loading plugins");
    pluginsModule = PyImport_ImportModule("core.plugins");
	PY_ERR(pluginsModule)
	pFunc = PyObject_GetAttrString(pluginsModule, "loadPlugins");
	PY_ERR(pFunc)
	if(!PyCallable_Check(pFunc))
	{
		fprintf(stderr, "Error: loadPlugins function could not be loaded.\n");
		return false;
	}
	pArgs = PyTuple_New(0);
	pValue = PyObject_CallObject(pFunc, pArgs);
	Py_DECREF(pArgs);
	Py_DECREF(pFunc);
	if(!pValue)
	{
		PyErr_Print();
		return false;
	}
	Py_DECREF(pValue);
	Py_DECREF(pluginsModule);
	
	return true;
}
	
void initPython(char *name) {
    logline(ACLOG_INFO,"Initalizing Python:");
    Py_SetProgramName(name);
    Py_Initialize();
    
    PyRun_SimpleString("import sys\nsys.path.append('./plugins');sys.path.append('./pyac_core')");
    
    logline(ACLOG_INFO,":  Loading acserver module");
    initModule();
    initCore();
}

void finalizePython() {
	Py_Finalize();
}