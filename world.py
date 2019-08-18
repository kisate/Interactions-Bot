import numpy

class World():
    def __init__(self, block_info):
        self.chunks = []
        self.block_info = block_info
    def get_chunk_coords(self, x, z):
        chunk_x = (x // 16)
        chunk_z = (z // 16)
        return (chunk_x, chunk_z)
    def get_block(self, x, y, z):
        coords = self.get_chunk_coords(x, z)
        return self.get_chunk_by_chunk_coords(*coords).get_block(x, y, z)
    def get_chunk_by_chunk_coords(self, chunk_x, chunk_z):
        for chunk in self.chunks:
            if chunk.x == chunk_x and chunk.z == chunk_z:
                return chunk
    def update_block(self, x, y, z, data, relative=True):
        coords = self.get_chunk_coords(x, z)
        self.get_chunk_by_chunk_coords(*coords).update_block(x, y, z, data, relative)
    def update_block_multi(self, chunk_x, chunk_z, records):
        chunk = self.get_chunk_by_chunk_coords(chunk_x, chunk_z)
        chunk.update_block_multi(records)
    
    def find_chunks_with_block(self, data):
        chunks = []
        for chunk in self.chunks:
            if data in chunk.blocks_in_chunk:
                chunks.append(chunk)
        return chunks
    
    def __str__(self):
        return str(self.chunks)
