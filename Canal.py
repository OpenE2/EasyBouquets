class Canal:
	def __init__(self,numero, nome,selected=False,hd=False):
		self. numero=numero
		self.nome=(nome.encode('utf-8').lower().strip())
		self.selected=selected
		self.hd=hd

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.nome==other.nome and self.numero==other.numero and self.hd==other.hd

	def __str__(self):
		return str(self.numero)+" - "+self.nome