#include "cube.h"

static PyObject *py_logline(PyObject *self, PyObject *args)
{
    char *s;
    int level = ACLOG_INFO;
    if(!PyArg_ParseTuple(args,  "s|i", &s, &level))
        return NULL;
    
    if (-1 < level && level < ACLOG_NUM) {
        logline(level,s);
    }
    
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef ModuleMethods[] = {
	{"log", py_logline, METH_VARARGS, "Logs a message."},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initModule()
{
	(void) Py_InitModule("acserver", ModuleMethods);
	return;
}