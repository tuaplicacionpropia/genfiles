#!/usr/bin/env python2.7
#coding:utf-8

import hjson
import os
import jinja2
import codecs
#import imp
import importlib

class JinjaGenFiles:

  def __init__ (self):
    pass

  def generate (self, templatePath, dataPath=None, outputPath=None):
    cwd = os.getcwd()
    #print(str(cwd))

    checkDataStr = True if type(dataPath) == str else False

    dataClass = None
    dataListClass = False
    itemClass = None
    if checkDataStr and dataPath.startswith("class://"):
      print("ES CLASS")
      dataPath = dataPath[8:]
      print("dataPath = " + dataPath)
      dataIdx = dataPath.find('?')
      if dataIdx > -1:
        dataArgs = dataPath[(dataIdx + 1):]
        print("dataArgs = " + dataArgs)
        arrayDataArgs = dataArgs.split('&')
        for itemArrayDataArgs in arrayDataArgs:
          valuesItemDataArg = itemArrayDataArgs.split('=')
          if valuesItemDataArg[0] == 'type':
            dataClass = valuesItemDataArg[1]
          if valuesItemDataArg[0] == 'list' and valuesItemDataArg[1] == 'true':
            dataListClass = True
        dataPath = dataPath[0:dataIdx]
    if dataClass is not None:
      classPkgIdx = dataClass.rfind(".")
      classPkg = dataClass[0:classPkgIdx]
      className = dataClass[(classPkgIdx+1):]

      #components = dataClass.split('.')
      '''
      mod = __import__(components[0]+"."+components[1])
      print(str(dir(mod)))
      for comp in components[2:]:
        print(str(comp))
        mod = getattr(mod, comp)
        print(str(dir(mod)))
      '''
      #mod = __import__(classPkg)
      mod = importlib.import_module(classPkg)
      #print(str(dir(mod)))
      #print("classPkg5 = " + str(classPkg))
      #print("className5 = " + str(className))
      itemClass = getattr(mod, className)
      #print(str(itemClass))
      '''
      try:
        fp, pathname, description = imp.find_module(classPkg)
        itemClass = imp.load_module("%s" % (dataClass), fp, pathname, description)
        print itemClass
      except Exception as e:
        print e
      '''

    if templatePath is not None and not os.path.isabs(templatePath):
      templatePath = os.path.join(cwd, templatePath)

    if checkDataStr and dataPath is not None and not os.path.isabs(dataPath):
      dataPath = os.path.join(cwd, dataPath)

    if outputPath is not None and not os.path.isabs(outputPath):
      outputPath = os.path.join(cwd, outputPath)

    baseDir = os.path.dirname(templatePath)
    templateName = os.path.basename(templatePath)

    data = None
    if checkDataStr and dataPath is not None:
      #print("load data path = " + dataPath)
      #data = dict(self.__loadObj__(dataPath))
      if itemClass is not None:
        if dataListClass:
          data = list()
          listData = self.__loadObj__(dataPath)
          for listDataItem in listData:
            dataItem = getattr(itemClass, 'load')(listDataItem)
            data.append(dataItem)
        else:
          data = getattr(itemClass, 'load')(dataPath)
      else:
        data = self.__loadObj__(dataPath)
      #print(str(data))
    else:
      data = dataPath

    file_loader = jinja2.FileSystemLoader(baseDir)
    env = jinja2.Environment(loader=file_loader, extensions=['jinja2.ext.do'])
    env.filters['myUpper'] = self.myUpper
    env.tests['verdadero'] = self.is_verdadero
    env.tests['falso'] = self.is_falso
    template = env.get_template(templateName)

    if outputPath is None:
      output = None
      if data is None:
        output = template.render()
      else:
        #print("render with data")
        output = template.render(data=data)
      print(output)
    else:
      stream = None
      if data is None:
        stream = template.stream()
      else:
        stream = template.stream(data=data)
      stream.dump(outputPath, encoding='utf-8')

  def __saveObj__ (self, path, obj):
    fp = codecs.open(path, mode='w', encoding='utf-8')
    hjson.dump(obj, fp)

  def __loadObj__ (self, path):
    result = None
    fp = codecs.open(path, mode='r', encoding='utf-8')
    result = hjson.load(fp)
    return result

  def myUpper(self, value, suffix='00'):
    suffix = suffix if suffix is not None else ''
    return value.upper() + suffix

  def is_verdadero(self, value):
    return True if value == 'True' else False

  def is_falso(self, value):
    return False if value == 'True' else True


def test():
  t = jinja2.Template("Hello {{ something }}!")
  print(t.render(something="World"))
  t = jinja2.Template("My favorite numbers: {% for n in range(1,10) %}{{n}} " "{% endfor %}")
  print(t.render())

def test2():
  file_loader = jinja2.FileSystemLoader('/media/jmramoss/ALMACEN/pypi/genfiles/genfiles')
  env = jinja2.Environment(loader=file_loader)
  template = env.get_template('hello.txt')
  output = template.render()
  print(output)

def test3():
  file_loader = jinja2.FileSystemLoader('/media/jmramoss/ALMACEN/pypi/genfiles/genfiles')
  env = jinja2.Environment(loader=file_loader)
  template = env.get_template('lamb.txt')
  output = template.render(name=u'Jesús')
  print(output)

def test4():
  person = {}
  person['name'] = u'Jesús'
  person['animal'] = u'murciélago'

  file_loader = jinja2.FileSystemLoader('/media/jmramoss/ALMACEN/pypi/genfiles/genfiles')
  env = jinja2.Environment(loader=file_loader)
  template = env.get_template('data.txt')
  output = template.render(data=person)
  print(output)

if True and __name__ == '__main__':
  tools = JinjaGenFiles()
  #tools.generate("hello.txt")
  #tools.generate("data.txt", dataPath="/media/jmramoss/ALMACEN/pypi/genfiles/genfiles/data.hjson")
  #tools.generate("data.txt", dataPath="/media/jmramoss/ALMACEN/pypi/genfiles/genfiles/data.hjson", outputPath="/media/jmramoss/ALMACEN/pypi/genfiles/genfiles/data.out")
  #tools.generate("data.txt", dataPath="data.hjson", outputPath="data3.out")
  tools.generate("templates/items.txt", dataPath="class://templates/items.hjson?type=genfiles.templates.Item&list=true", outputPath="templates/items.out")
  #test4()
  #print("HOLA2")
