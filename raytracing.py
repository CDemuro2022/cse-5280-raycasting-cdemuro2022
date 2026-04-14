import numpy as np               # Numpy library
from PIL import Image as im      # Basic image processing library

class Ray:
    """A class representing a ray (line in space).

    Uses the parametric representation of a line, p(t) = e + (s - e)*t.

    The ray passes through the following two points:

    e = [e_u, e_v, e_w] representing the eye location in 3-D, and
    s = [e_u, e_v, e_w] representing a point on the image plane.

    Attributes:
        e: 3x1 np.array, e.g.,
        s: 3x1 np.array
    """

    def __init__(self, e, s):
        """Constructor method

        Args:
            e (3x1 np.array): Eye location
            s (3x1 np.array): Point on the image plane
        """
        self.e = e
        self.s = s


    def get3DPoint(self, t):
        """Calculates the location of a 3-D point along the ray given t.

        Args:
            t (float): Parameter of the ray equation
        Returns:
            p (3x1 nd.array): Point p(t) = e + (s - e) * t.
        """
        p = self.e + (self.s - self.e) * t    # p(t) = e + (s - e) * t

        return p


class Sphere:
    """A class representing a Sphere.

    Attributes:
        Center (3x1 np.ndarray): Center of the sphere in 3-D
        Radius (float): Radius of the sphere
        Color (3x1 np.ndarray): (Solid) Color of the sphere's surface Color = [ red, green, blue]
    """

    def __init__(self, c, r, k, reflectivity=0.2, transparency=0.0, ior=1.0, roughness=0.0):
        self.Center = c
        self.Radius = r
        self.Color = k
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.ior = ior   # index of refraction (air=1.0, glass≈1.5)
        self.roughness = roughness

    def Intersect(self, ray):
        """Calculates the intersection of this sphere and the ray provided as input

        Args:
            ray (Ray object)  p(t) = e + (s - e) * t
        Returns:
            t (float): distance (line parameter) from the eye to the intersection point along the ray
        """
        # ray: ray object  p(t) = e + (s - e) * t

        # For calculations, I prefer to use the notation
        # similar to the one in the slides or associated paper.
        d = ray.s - ray.e  # Direction of the ray
        e = ray.e          # Ray's starting point

        c = self.Center  # Sphere center
        r = self.Radius  # Sphere radius

        # Check whether the ray intersects the sphere
        A = np.dot(d, d)
        B = 2.0 * np.dot(d, (e - c))
        C = np.dot((e - c), (e - c)) - r * r

        #delta = B*B - A * C
        delta = B*B - 4.0 * A * C
        if delta < 0:
            return float("inf")         # Ray didn't intersect sphere
        else:
            t1 = (-B - np.sqrt(delta)) / (2.0 * A)
            t2 = (-B + np.sqrt(delta)) / (2.0 * A)

            t_candidates = [t for t in (t1, t2) if t > 1e-5]

            if not t_candidates:
                return float("inf")

            return min(t_candidates)

    def get_normal(self, p):
        """ Calculates the surface normal at the point p on the sphere.
            It assumes that p is on the sphere!!!
        Args:
            p (3x1 np.ndarray): 3-D point on the sphere
        Returns:
            n (3x1 np.ndarray): Normalized (unit) normal vector at point p
        """

        n = (p - self.Center) / np.linalg.norm(p - self.Center)

        return n

class HitInformation:
    """A class representing the all the information of objects intersected by a given ray.

    Attributes:
        Object (python class of object): e.g., sphere, cylinder, cone, plane

        p (3x1 np.ndarray): 3-D coordinates of the intersection point
    """
    def __init__(self, intersected_object, intersecton_point):
        self.Object = intersected_object
        self.p = intersecton_point



class Camera:
    """A class representing the camera.

    This camera consists of the focal length, the image matrix, and functions
    that convert pixel coordinates to geometric (u,v,w)-coordinates.

    Attributes:
        f (float): Camera's focal distance

        nrows (int): Image horizontal resolution in pixels
        ncols (int): Image vertical resolution in pixels
        I (np.ndarray of size nrows x ncols)
    """
    # Number of color channels
    nchannels = 3    # channels (RGB)

    # Eye location (i.e., viewer)
    eye = np.array((0.0, 0.0, 0.0)).transpose()


    def __init__(self, f, nrows, ncols):
        # f: Focal distance
        self.f = f
        self.nrows = nrows    # Image resolution in pixels
        self.ncols = ncols

        # Initialize image matrix
        self.I = np.zeros([self.nrows, self.ncols, self.nchannels])

    'Ray-sphere intersection. It returns the smallest t. '
    def ij2uv(self, i, j):
        u =  (j + 0.5) - self.ncols/2
        v = -(i + 0.5) + self.nrows/2

        return u,v

    def constructRayThroughPixel(self, i, j):
        # Construct ray through pixel (i,j)
        u,v = self.ij2uv(i, j)
        s = np.array((u, v, -self.f)).transpose()
        ray = Ray(self.eye, s)

        return ray

class Scene:
    """A class representing the whole scene, i.e., objects in the scene.

    I wanted Scene to consist of the entire scene that consists of
    all objects (e.g., spheres, planes, triangles, cilinders).

    Here is just a preliminary attempt of implementing a list of objects.

    Attributes:
        Object (python class of object): e.g., sphere, cylinder, cone, plane

        p (3x1 np.ndarray): 3-D coordinates of the intersection point
    """


    def __init__(self, theCamera):

        self.theCamera = theCamera   # I think I need the camera because it has the eye location

        self.light_pos = np.array([0, 200, -300])
        self.light_radius = 80.0

        # I simply implement this class as a list of geometrical objects.
        list = []

        # Object 1
        Center = np.array((-90, 0, -800.0)).transpose()
        Radius = 80.0
        Color = np.array((255, 0, 0)).transpose()
        list.append(Sphere(Center, Radius, Color, roughness=0.5))

        # Object 2
        Center = np.array((90, 0, -400.0)).transpose()
        Radius = 80.0
        Color = np.array((0, 255, 0)).transpose()
        list.append(Sphere(Center, Radius, Color))


        # Ground plane
        p0 = np.array((0, -100, 0))          # point on plane
        n  = np.array((0, 1, 0))             # upward normal
        color = np.array((200, 200, 200))    # light gray

        list.append(Plane(p0, n, color, reflectivity=0.6))

        Center = np.array((45, 0, -300.0))
        Radius = 25.0
        Color = np.array((100, 200, 255))

        list.append(
            Sphere(
            Center,
            Radius,
            Color,
            reflectivity=0.1,
            transparency=0.7,
            ior=1.5
        )
)

        # List of objects in the scene
        self.scene_objects = list

    def find_intersection(self, ray):
        closest_t = float('inf')
        closest_hit = None

        for surface in self.scene_objects:
            t = surface.Intersect(ray)
            if 1e-5 < t < closest_t:
                closest_t = t
                p = ray.get3DPoint(t)
                closest_hit = HitInformation(surface, p)

        return closest_hit

    def get_color(self, hit_list):
        """Returns the `seen' by the visual ray. This is the sum of all colors * shading
        """
        pixelColor =  np.array((0.0, 0.0, 0.0))  # Initial color is black
        for hit in hit_list:                    # Loop through hits

            # Get surface normal at the intersection point
            n = hit.Object.get_normal(hit.p)
            # Calculate diffuse shading
            diffuse_shading = max(0, np.dot(self.light_source_1, n))

            # Ambient light component
            ambient_color = hit.Object.Color * 0.3

            # Calculate specular component
            v = self.theCamera.eye - hit.p
            h = v + self.light_source_1
            h = h / np.linalg.norm(h)

            specular_component = max(0, np.dot(n, h)) ** 64
            specular_component = 2


            pixelColor += ambient_color + hit.Object.Color * diffuse_shading  + hit.Object.Color * specular_component# Color of the intersected object (at the intersection point)

            # Each color component is in the range [0..255].
            pixelColor =  pixelColor / len(self.scene_objects)

            #np.linalg.norm(pixelColor)


        return pixelColor

    def trace_ray(self, ray, depth=0, max_depth=3):
        if depth > max_depth:
            return np.array((0, 0, 0))

        hit = self.find_intersection(ray)
        if hit is None:
            return np.array((0, 0, 0))  # background color

        obj = hit.Object
        p = hit.p
        n = obj.get_normal(p)

        # --- Local illumination ---
        base_light_dir = self.light_pos - p
        base_light_dir = base_light_dir / np.linalg.norm(base_light_dir)

        light_samples = self.sample_light(n_samples=16)

        shadow_sum = 0.0

        for lp in light_samples:
            light_dir = lp - p
            dist = np.linalg.norm(light_dir)
            light_dir = light_dir / dist

            # shadow ray
            shadow_ray = Ray(p + 1e-4 * light_dir, p + light_dir)

            hit = self.find_intersection(shadow_ray)

            # if nothing blocks light OR blocker is beyond light
            if hit is None:
                shadow_sum += 1.0
            else:
                hit_dist = np.linalg.norm(hit.p - p)
                if hit_dist > dist:
                    shadow_sum += 1.0
                # else blocked → contributes 0

        shadow_factor = shadow_sum / len(light_samples)

        diffuse = shadow_factor * max(0, np.dot(n, base_light_dir))
        ambient = obj.Color * 0.3

        color = ambient + obj.Color * diffuse

        v = self.theCamera.eye - p
        v = v / np.linalg.norm(v)

        h = (v + light_dir)
        h = h / np.linalg.norm(h)

        specular = max(0, np.dot(n, h)) ** 32

        color += 255 * specular

        # --- Reflection ---
        reflectivity = 0.2  # you can store this in the object

        if reflectivity > 0:
            d = ray.s - ray.e
            d = d / np.linalg.norm(d)

            # Reflection direction
            r = d - 2 * np.dot(d, n) * n
            r = r / np.linalg.norm(r)


        # --- glossy reflection rays ---
        roughness = getattr(obj, "roughness", 0.0)

        if roughness > 0:
            rays = self.glossy_reflection(r, roughness=roughness, samples=12)

            reflected_color = np.array((0.0, 0.0, 0.0))

            for rr in rays:
                epsilon = 1e-5
                origin = p + epsilon * rr
                glossy_ray = Ray(origin, origin + rr)

                reflected_color += self.trace_ray(glossy_ray, depth + 1, max_depth)

            reflected_color /= len(rays)
        else:
        	# fallback: perfect mirror (your original behavior)
            reflected_ray = Ray(p + 1e-5 * r, p + r)
            reflected_color = self.trace_ray(reflected_ray, depth + 1, max_depth)

        # --- Refraction ---
        transparency = getattr(obj, "transparency", 0.0)
        ior = getattr(obj, "ior", 1.0)

        refracted_color = np.array((0.0, 0.0, 0.0))

        if transparency > 0:
            d = ray.s - ray.e
            d = d / np.linalg.norm(d)

            refr_dir = self.refract(d, n, ior)

            if refr_dir is not None:
                epsilon = 1e-5
                refr_origin = p - epsilon * n  # step inside object

                refracted_ray = Ray(refr_origin, refr_origin + refr_dir)

                refracted_color = self.trace_ray(refracted_ray, depth + 1, max_depth)

        color = (
            (1 - reflectivity - transparency) * color +
            reflectivity * reflected_color +
            transparency * refracted_color
        )

        return np.clip(color, 0, 255)

    def refract(self, d, n, ior):
        d = d / np.linalg.norm(d)
        n = n / np.linalg.norm(n)

        cosi = np.clip(np.dot(d, n), -1, 1)
        etai = 1
        etat = ior

        if cosi < 0:
            cosi = -cosi
        else:
            n = -n
            etai, etat = etat, etai

        eta = etai / etat
        k = 1 - eta * eta * (1 - cosi * cosi)

        if k < 0:
            return None  # total internal reflection

        return eta * d + (eta * cosi - np.sqrt(k)) * n

    def glossy_reflection(self, r, roughness=0.2, samples=8):
        r = r / np.linalg.norm(r)

        # build a random basis around reflection direction
        def random_perturb(v):
            rand = np.random.normal(size=3)
            rand = rand - np.dot(rand, v) * v
            rand = rand / np.linalg.norm(rand)

            new_dir = v + roughness * rand
            return new_dir / np.linalg.norm(new_dir)

        return [random_perturb(r) for _ in range(samples)]

    def sample_light(self, n_samples=16):
        samples = []

        for _ in range(n_samples):
            # random point on unit disk
            theta = 2 * np.pi * np.random.rand()
            r = self.light_radius * np.sqrt(np.random.rand())

            offset = np.array([
                r * np.cos(theta),
                0,
                r * np.sin(theta)
            ])

            samples.append(self.light_pos + offset)

        return samples

class Plane:
    def __init__(self, p0, n, color, reflectivity=0.5):
        self.p0 = p0
        self.n = n / np.linalg.norm(n)
        self.Color = color
        self.reflectivity = reflectivity

    def Intersect(self, ray):
        d = ray.s - ray.e
        denom = np.dot(self.n, d)

        if abs(denom) < 1e-6:
            return float('inf')  # Parallel → no hit

        t = np.dot(self.n, (self.p0 - ray.e)) / denom

        if t > 1e-5:
            return t
        else:
            return float('inf')

    def get_normal(self, p):
        return self.n


# Create camera (and image resolution)
nrows = 512
ncols = 512
# Focal distance
f = 250.0

myCamera = Camera(f, nrows, ncols)

# Create the scene (collection of objects - hardcoded for simplicity)
theScene = Scene(myCamera)

camera_positions = [
    np.array((0, 0, 0)),
    np.array((100, 50, 0)),
    np.array((-150, 80, 50)),
    np.array((0, 200, 100)),
]

for idx, pos in enumerate(camera_positions):
    myCamera.eye = pos

    # reset image
    myCamera.I = np.zeros([nrows, ncols, 3])

    for i in range(nrows):
        for j in range(ncols):
            ray = myCamera.constructRayThroughPixel(i, j)
            color = theScene.trace_ray(ray, depth=0)
            myCamera.I[i, j, :] = color

    out_image = im.fromarray(np.uint8(myCamera.I))
    out_image.save(f'render_{idx}.png')