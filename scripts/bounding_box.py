
import sys
import json

# bounding box - represents a bounding box in an image
class BoundingBox:
    from_x = 0
    from_y = 0
    to_x = 0
    to_y = 0

    def __init__(self, from_x = (-sys.maxint - 1), to_x = sys.maxint, from_y = (-sys.maxint - 1), to_y = sys.maxint):
        self.from_x = float(from_x)
        self.to_x = float(to_x)
        self.from_y = float(from_y)
        self.to_y = float(to_y)
        if not self.validate():
            raise "Invalid bounding box values: {0}, {1}, {2}, {3} (should be {0} < {1}, and {2} < {3}".format(
                self.from_x, self.from_y, self.to_x, self.to_y) 

    @classmethod
    def fromList(cls, bbox_list):
        return cls(bbox_list[0], bbox_list[1], bbox_list[2], bbox_list[3])


    @classmethod
    def fromStr(cls, bbox_str):
        return cls.fromList(bbox_str.split(" "))

    def validate(self):
        # TODO: check that the bounding box values are valid
        if (self.from_x > self.to_x) or (self.from_y > self.to_y):
            return False
        return True

    def overlap(self, other_bbox):
        # Returns true if there is intersection between the bboxes or a full containment
        if (self.from_x < other_bbox.to_x) and (self.to_x > other_bbox.from_x) and \
           (self.from_y < other_bbox.to_y) and (self.to_y > other_bbox.from_y):
            return True
        return False

    def extend(self, other_bbox):
        # updates the current bounding box by extending it to include the other_bbox
        if self.from_x > other_bbox.from_x:
            self.from_x = other_bbox.from_x
        if self.from_y > other_bbox.from_y:
            self.from_y = other_bbox.from_y
        if self.to_x < other_bbox.to_x:
            self.to_x = other_bbox.to_x
        if self.to_y < other_bbox.to_y:
            self.to_y = other_bbox.to_y

    def toStr(self):
        return '{0} {1} {2} {3}'.format(self.from_x, self.to_x, self.from_y, self.to_y)

    def toArray(self):
        return [self.from_x, self.to_x, self.from_y, self.to_y]

    @classmethod
    def load_tiles(cls, tiles_spec_fname):
        all_bboxes = []
        with open(tiles_spec_fname, 'r') as data_file:
            data = json.load(data_file)
        for tile in data:
            tile_bbox = BoundingBox.fromList(tile['bbox'])
            all_bboxes.append(tile_bbox)
        return all_bboxes

    @classmethod
    def read_bbox(cls, tiles_spec_fname):
        all_bboxes = BoundingBox.load_tiles(tiles_spec_fname)
        # merge the bounding boxes to a single bbox
        if len(all_bboxes) > 0:
            ret_val = all_bboxes[0]
            for bbox in all_bboxes:
                ret_val.extend(bbox)
            return ret_val.toArray()
        return None

    def union(self, other_bbox):
        return BoundingBox(min(self.from_x, other_bbox.from_x),
                           max(self.to_x, other_bbox.to_x),
                           min(self.from_y, other_bbox.from_y),
                           max(self.to_y, other_bbox.to_y))

    def intersect(self, other_bbox):
        return BoundingBox(max(self.from_x, other_bbox.from_x),
                           min(self.to_x, other_bbox.to_x),
                           max(self.from_y, other_bbox.from_y),
                           min(self.to_y, other_bbox.to_y))

    def contains(self, pts):
        '''return a mask of points that are within the box.  pts.shape = (..., 2)'''
        return ((pts[:, 0] >= self.from_x) & (pts[:, 0] <= self.to_x) &
                (pts[:, 1] >= self.from_y) & (pts[:, 1] <= self.to_y))

    def expand(self, scale=None, offset=None):
        assert (scale is not None) or (offset is not None)
        if scale is not None:
            x_delta = scale * (self.to_x - self.from_x)
            y_delta = scale * (self.to_y - self.from_y)
            return BoundingBox(self.from_x - x_delta, self.to_x + x_delta,
                               self.from_y - y_delta, self.to_y + y_delta)
        else:
            return BoundingBox(self.from_x - offset, self.to_x + offset,
                               self.from_y - offset, self.to_y + offset)
