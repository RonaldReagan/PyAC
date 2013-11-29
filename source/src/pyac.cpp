#include "cube.h"

#define PY_ERR(x) \
	if(!x) \
	{ \
		if(PyErr_Occurred()) \
			PyErr_Print(); \
			return false; \
	}

PyMODINIT_FUNC initModule();

static PyObject *eventsModule, *triggerEventFunc, *triggerPolicyEventFunc, *updateFunc;

bool initCore() {
    PyObject *pFunc = 0, *pArgs = 0, *pValue = 0, *pluginsModule = 0, *configModule;
    
    logline(ACLOG_INFO,":  Loading global config");
	configModule = PyImport_ImportModule("core.config");
	PY_ERR(configModule)
	
    eventsModule = PyImport_ImportModule("core.events");
	PY_ERR(eventsModule)
	triggerEventFunc = PyObject_GetAttrString(eventsModule, "triggerServerEvent");
	PY_ERR(triggerEventFunc);
	if(!PyCallable_Check(triggerEventFunc))
	{
		fprintf(stderr, "Error: triggerEvent function could not be loaded.\n");
		return false;
	}
	triggerPolicyEventFunc = PyObject_GetAttrString(eventsModule, "triggerPolicyEvent");
	PY_ERR(triggerPolicyEventFunc);
	if(!PyCallable_Check(triggerPolicyEventFunc))
	{
		fprintf(stderr, "Error: triggerPolicyEvent function could not be loaded.\n");
		return false;
	}
	updateFunc = PyObject_GetAttrString(eventsModule, "update");
	PY_ERR(updateFunc);
	if(!PyCallable_Check(updateFunc))
	{
		fprintf(stderr, "Error: update function could not be loaded.\n");
		return false;
	}
	
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
	Py_DECREF(configModule);
	
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

PyObject *callPyFunc(PyObject *func, PyObject *args)
{
	PyObject *val;
	val = PyObject_CallObject(func, args);
	Py_DECREF(args);
	if(!val)
		PyErr_Print();
	return val;
}

bool triggerFuncEvent(const char *name, vector<PyObject*> args, PyObject *func)
{
	PyObject *pArgs, *pArgsArgs, *pName, *pValue;

	if(!func)
	{
		logline(ACLOG_ERROR, "Python Error: Invalid handler to triggerEvent function.");
		return false;
	}
	pArgs = PyTuple_New(2);
	pName = PyString_FromString(name);
	PY_ERR(pName)
	PyTuple_SetItem(pArgs, 0, pName);
	if(args.length())
	{
		pArgsArgs = PyTuple_New(args.length());
		loopv(args)
		{
			PyTuple_SetItem(pArgsArgs, i, args[i]);
		}
	}
	else
		pArgsArgs = PyTuple_New(0);
	
	PyTuple_SetItem(pArgs, 1, pArgsArgs);
	pValue = callPyFunc(func, pArgs);
	if(!pValue)
	{
		logline(ACLOG_ERROR, "Error triggering event.");
		return false;
	}
	if(PyBool_Check(pValue))
	{
		bool ret = (pValue == Py_True);
		Py_DECREF(pValue);
		return ret;
	}
	Py_DECREF(pValue);
	return true;
}

#undef PY_ERR

bool triggerFunc(const char *name, bool policy, const char *sig, ...) {
    va_list args;
    va_start(args,sig);
    
    vector<PyObject*> PyArgs;
    PyObject *pyo;
    
    for (int i=0;i<(int)strlen(sig);i++) {
        if (sig[i] == 's') {
            char *s = va_arg(args,char*);
            pyo = PyString_FromString(s);
            PyArgs.add(pyo);
        }
        else if (sig[i] == 'i') {
            int i = va_arg(args,int);
            pyo = PyInt_FromLong(i);
            PyArgs.add(pyo);
        }
        else if (sig[i] == 'f') {
            double f = va_arg(args,double);
            pyo = PyFloat_FromDouble(f);
            PyArgs.add(pyo);
        }
    }
    
    va_end(args);
    
    if (policy) {
        return triggerFuncEvent(name,PyArgs,triggerPolicyEventFunc);
    }
    else {
        return triggerFuncEvent(name,PyArgs,triggerEventFunc);
    }
}