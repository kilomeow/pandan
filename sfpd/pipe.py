class Pipeable:
   def extend(self, pipe):
       raise NotImplemented

   @property
   def content(self):
       raise NotImplemented

   def _direct_extend(self, pipe):
       pipe.chain.extend(self.content)


class PipeableFunc(Pipeable):
   def __init__(self, func):
       self.func = func

   def extend(self, pipe):
      pipe.chain.append(self.func)
      return pipe


class AbstractPipe(Pipeable):
    def __init__(self):
        raise NotImplemented

    def copy(self):
       raise NotImplemented

    @property
    def chain(self):
       raise NotImplemented

    @staticmethod
    def parse(pipeable):
        if isinstance(pipeable, Pipeable):
            return pipeable
        elif callable(pipeable):
            return PipeableFunc(pipeable)
        else:
            raise TypeError(f"Couldn't pass {type(pipeable)} to pipe because it's not Pipeable neither callable")

    @classmethod
    def new_from_pipeable(cls, pipeable):
        pipeable = cls.parse(pipeable)
        newpipe = cls()
        pipeable.extend(newpipe)
        return newpipe

    def append_right(self, pipeable):
        pipeable = self.parse(pipeable)
        newpipe = self.copy()
        return pipeable.extend(newpipe)

    def append_left(self, pipeable):
        pipeable = self.parse(pipeable)
        newpipe = self.new_from_pipeable(pipeable)
        return self.extend(newpipe)

    __rshift__ = append_right
    __lshift__ = append_left


    def apply(self, *args, **kwargs):
        raise NotImplemented

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)
      


class PipeType(AbstractPipe, Pipeable):
   def __init__(self):
       self._chain = []

   @property
   def chain(self):
      return self._chain

   def copy(self):
       newpipe = type(self)()
       newpipe._chain = self._chain[:]
       return newpipe

   def extend(self, pipe):
       pipe.chain.extend(self.chain)
       return pipe

   def apply(self, *args, **kwargs):
       if len(self.chain) == 0:
           raise TypeError(f"Couldn't apply empty pipe")
       else:
           t = self.chain[0](*args, **kwargs)
           for f in self.chain[1:]:
               t = f(t)
           return t


class AbstractApplicative:
   def to(self, pipe):
      raise NotImplemented

   def __or__(self, pipe):
      return self.to(pipe)
   

class MapApplicative(AbstractApplicative):
   def __init__(self, seqarg):
       self.seqarg = seqarg

   def to(self, pipe):
       return list(map(pipe, self.seqarg))


class MetaMap(Pipeable):
    def extend(self, pipe):
        def map_apply(argseq):
            return map(pipe, argseq)
        return PipeType.new_from_pipeable(map_apply)

    def __call__(self, argseq):
       return MapApplicative(argseq)


Map = MetaMap()


class Apply(AbstractApplicative):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def to(self, pipe):
        return pipe.apply(*self.args, **self.kwargs)

    __or__ = to


Pipe = PipeType()
