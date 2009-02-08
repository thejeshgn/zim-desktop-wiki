# -*- coding: utf8 -*-

# Copyright 2008 Jaap Karssenberg <pardus@cpan.org>

'''Test cases for basic stores modules.'''

import tests

from zim.fs import *
from zim.notebook import Notebook
import zim.stores

# TODO test if store implements get_root() and get_namespace() correctly

class TestStoresMemory(tests.TestCase):
	'''Test the store.memory module'''

	def setUp(self):
		'''Initialise a fresh notebook'''
		store = zim.stores.get_store('memory')
		self.store = store.Store(namespace='', notebook=Notebook())
		self.index = set()
		for name, text in tests.get_notebook_data('wiki'):
			self.store._set_node(name, text)
			self.index.add(name)
		self.normalize_index()

	def normalize_index(self):
		'''Make sure the index conains namespaces for all page names'''
		pages = self.index.copy()
		for name in pages:
			parts = name.split(':')
			parts.pop()
			while len(parts) > 1:
				self.index.add(':'.join(parts))
				parts.pop()

	def testIndex(self):
		'''Test we get a proper index'''
		names = set()
		for page in self.store.get_root().walk():
			names.add( page.name )
		#import pprint
		#pprint.pprint(self.index)
		#pprint.pprint(names)
		self.assertEqual(names, self.index)

	def testResolveName(self):
		'''Test store.resolve_name().'''
		#~ print '\n'+'='*10+'\nSTORE: %s' % self.store

		# First make sure basic list function is working
		def list_pages(name):
			for page in self.store.list_pages(name):
				yield page.basename
		self.assertTrue('Test' in list_pages(''))
		self.assertTrue('foo' in list_pages(':Test'))
		self.assertTrue('bar' in list_pages(':Test:foo'))
		self.assertFalse('Dus' in list_pages(':Test:foo'))

		# Now test the resolving algorithm - only testing low level
		# function in store, so path "anchor" does not work, search
		# is strictly right to left through the namespace, if any
		for link, namespace, name in (
			('BAR','Test:foo','Test:foo:bar'),
			('test',None,'Test'),
			('test','Test:foo:bar','Test'),
			('FOO:Dus','Test:foo:bar','Test:foo:Dus'),
			# FIXME more ambigous test data
		):
			#~ print '-'*10+'\nLINK %s (%s)' % (link, namespace)
			r = self.store.resolve_name(link, namespace=namespace)
			#~ print 'RESULT %s' % r
			self.assertEqual(r, name)

	#~ def testResolveFile(self):
		#~ '''Test store.resolve_file()'''

	# TODO test getting a non-existing page
	# TODO test if children uses namespace objects
	# TODO test move, delete, read, write


class TestFiles(TestStoresMemory):
	'''Test the store.files module'''

	def setUp(self):
		TestStoresMemory.setUp(self)
		tmpdir = tests.create_tmp_dir('stores_TestFiles')
		self.dir = Dir([tmpdir, 'store-files'])
		self.mem = self.store
		store = zim.stores.get_store('files')
		self.store = store.Store(
			namespace='', notebook=Notebook(),
			dir=self.dir )
		for page in self.mem.get_root().walk():
			if page.isempty():
				continue
			self.store.clone_page(page.name, page)

	# TODO test move, delete, read, write