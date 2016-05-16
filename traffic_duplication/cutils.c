#include <Python.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>

static PyObject * py_create_packet_counter(PyObject *self, PyObject *args) {
	char *name;
	PyArg_ParseTuple(args, "s", &name);
	
	int fd = shm_open(name, O_RDWR|O_CREAT, S_IRUSR|S_IWUSR);
	if (fd < 0) {
		perror("shm_open");
		return Py_BuildValue("i", -1);
	}
	int rv = ftruncate(fd, 8);
	if (rv != 0) {
		perror("ftruncate");
		close(fd);
		return Py_BuildValue("i", -1);
	}

	close(fd);
	return Py_BuildValue("i", rv);
}

static PyObject * py_get_packet_counter(PyObject *self, PyObject *args) {
	char *name;
	PyArg_ParseTuple(args, "s", &name);

	int fd = shm_open(name, O_RDWR, S_IWUSR|S_IRUSR);
	if (fd < 0) {
	  perror("shm_open");
	  return Py_BuildValue("i", -1);
	}
	
	unsigned long long *shared_ctr = (unsigned long long *)mmap(NULL, 8, PROT_WRITE, MAP_SHARED, fd, 0);
	if ((void *)shared_ctr == MAP_FAILED) {
	  perror("mmap srv");
	  close(fd);
	  return Py_BuildValue("i", -1);
	}

	unsigned long long rv = *shared_ctr;
	if (munmap(shared_ctr, 8)) {
	  perror("munmap");
	  close(fd);
	  return Py_BuildValue("i", -1);
	}

	close(fd);
	return Py_BuildValue("K", rv);
}

static PyMethodDef cutils_methods[] = {
	{"get_packet_counter", py_get_packet_counter, METH_VARARGS},
	{"create_packet_counter", py_create_packet_counter, METH_VARARGS},
	{NULL, NULL}
};

void initcutils() {
	(void)Py_InitModule("cutils", cutils_methods);
}
