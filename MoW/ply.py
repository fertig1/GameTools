from __future__ import print_function
from __future__ import division

from builtins import hex
from builtins import range
from builtins import object
from past.utils import old_div
import struct

# constants
PLYMAGICK = "EPLYBNDS"
SUPPORTED_ENTRY = ["SKIN", "MESH", "VERT", "INDX"]
SUPPORTED_FORMAT = [0x0644, 0x0604, 0x0404, 0x0704, 0x0744, 0x0C14]

class PLY(object):
    def __init__(self, path, translate_uv_y=False):
        self.path = path
        self.translate_uv_y = translate_uv_y
        self.indeces = []
        self.positions = []
        self.normals = []
        self.UVs = []
        self.open(self.path)
        self.material_info = 0x0000        
        
    def open(self, peek=False, verbose=False):
        with open(self.path, "rb") as f:
            # read header
            magick, = struct.unpack("8s", f.read(8))
            if magick != PLYMAGICK:
                raise Exception("Unsupported format")
            x1, y1, z1, x2, y2, z2 = struct.unpack("ffffff", f.read(24))
            while True:
                entry, = struct.unpack("4s", f.read(4))
                print("Found entry %s at %s" % (entry, hex(f.tell())) )
                if not(entry in SUPPORTED_ENTRY):
                    raise Exception("Unsupported entry type")
                if entry == SUPPORTED_ENTRY[0]: #SKIN
                    # read the number of skins
                    skins, = struct.unpack("<I", f.read(4))
                    print("Number of skins: %i at %s" % (skins, hex(f.tell())))
                    for i in range(0, skins):
                      skin_name_length, = struct.unpack("B", f.read(1))
                      print("Skin name length:", hex(skin_name_length))
                      skin_name = f.read(skin_name_length)
                      print("Skin name:", skin_name)
                if entry == SUPPORTED_ENTRY[1]: #MESH
                    # read some unknown data
                    f.read(0x8)
                    triangles, = struct.unpack("<I", f.read(4))
                    print("Number of triangles:",triangles)
                    self.material_info, = struct.unpack("<I", f.read(4))
                    print("Material info:", hex(self.material_info))
                    if self.material_info in SUPPORTED_FORMAT:
                        if self.material_info == 0x0404:
                            pass
                        elif self.material_info == 0x0C14:
                            pass
                        else:
                            vert = f.read(0x4)
                    else:
                        raise Exception("Unsupported material type")
                    material_name_length, = struct.unpack("B", f.read(1))
                    print("Material name length:", hex(material_name_length))
                    material_file = f.read(material_name_length)
                    print("Material file:", material_file)
                    # read some more unknown data
                    if self.material_info == 0x0C14:
                      f.read(3)
                if entry == SUPPORTED_ENTRY[2]: #VERT
                    verts, = struct.unpack("<I", f.read(4))
                    print("Number of verts: %i at %s" % (verts, hex(f.tell())))
                    vertex_description, = struct.unpack("<I", f.read(4))
                    print("Vertex description:", hex(vertex_description))
                    for i in range(0, verts):
                        if vertex_description == 0x00010024:
                            vx,vy,vz,nx,ny,nz,U,V = struct.unpack("ffffff4xff", f.read(36))
                        elif vertex_description == 0x00070020:
                            vx,vy,vz,nx,ny,nz,U,V = struct.unpack("ffffffff", f.read(32))
                        elif vertex_description == 0x00070028:
                            vx,vy,vz,nx,ny,nz,U,V = struct.unpack("ffffffff8x", f.read(40))
                        elif vertex_description == 0x00070030:
                            vx,vy,vz,nx,ny,nz,U,V = struct.unpack("ffffffff16x", f.read(48))
                        else:
                            raise Exception("Unknown format: %s" % hex(vertex_description))
                        if verbose:
                            print("Vertex %i: " % i,vx,vy,vz)
                        self.positions.append((vx,vy,vz))
                        self.normals.append((nx,ny,nz))
                        if not self.translate_uv_y:
                            self.UVs.append((U,V))
                        else:
                            self.UVs.append((U,V+1.0))
                    print("Vertex info ends at:",hex(f.tell()))
                if entry == SUPPORTED_ENTRY[3]: #INDX
                    idx_count, = struct.unpack("<I", f.read(4))
                    print("Indeces:", idx_count)
                    for i in range(0, old_div(idx_count,3)):
                        i0,i1,i2 = struct.unpack("<HHH", f.read(6))
                        if verbose:
                            print("Face %i:" % i,i0,i1,i2)
                        if self.material_info == 0x0744:
                          self.indeces.append((i2,i1,i0))
                        else:
                          self.indeces.append((i0,i1,i2))
                    print("Indces end at", hex(f.tell()-1))
                    break

    def dump(self, outfile):
        print("Dumping to OBJ")
        with open(outfile, "wb") as f:
            for p in self.positions:
                f.write('{:s} {:f} {:f} {:f}\n'.format("v", *p))
            for UV in self.UVs:
                u = UV[0]
                v = 1.0 - UV[1]
                f.write('{:s} {:f} {:f}\n'.format("vt", u, v))
            for n in self.normals:
                f.write('{:s} {:f} {:f} {:f}\n'.format("vn", *n))
            for idx in self.indeces:
                new_idx = [x+1 for x in idx]
                # change vertex index order by swapping the first and last indeces
                f.write('{:s} {:d}/{:d}/{:d} {:d}/{:d}/{:d} {:d}/{:d}/{:d}\n'.format("f", new_idx[2], new_idx[2],
                new_idx[2], new_idx[1], new_idx[1], new_idx[1], new_idx[0], new_idx[0], new_idx[0]))
