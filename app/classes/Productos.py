from app.classes.Sucursal import Sucursal
from app.classes.Categorias import Categorias
from app.classes.TallaProducto import TallaProducto
from app.classes.Activerecord import Activerecord
from app.classes.ColorProducto import ColorProducto

class Producto(Activerecord):
    TABLA = 'producto'  
    nombre_id = 'id_producto'
    columnas_db = [
        'id_producto', 'nombre', 'descripcion', 'imagen', 'fecha_creacion',
        'genero', 'precio', 'para', 'id_sucursal', 'id_categoria','banner_producto'
    ]
    errores = [] 

    def __init__(self, id_producto=None, nombre=None, descripcion=None, imagen=None,
                 fecha_creacion=None, genero=None, precio=None, para=None,
                 id_sucursal=None, id_categoria=None,banner_producto=None):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.imagen = imagen
        self.fecha_creacion = fecha_creacion
        self.genero = genero
        self.precio = precio
        self.para = para
        self.id_sucursal = id_sucursal
        self.id_categoria = id_categoria
        self.banner_producto = banner_producto


    def validar(self) -> bool:
        self.errores = []
        if not self.nombre:
            self.errores.append("El nombre es obligatorio.")
        if not self.precio or self.precio <= 0:
            self.errores.append("El precio debe ser un número positivo.")
        if not self.id_sucursal:
            self.errores.append("La sucursal es obligatoria.")
        if not self.id_categoria:
            self.errores.append("La categoría es obligatoria.")
        if not self.genero:
            self.errores.append("El género es obligatorio.")
        if not self.descripcion:
            self.errores.append("La descripción es obligatoria.")
        if not self.imagen:
            self.errores.append("La imagen es obligatoria.")
        if not self.fecha_creacion:
            self.errores.append("La fecha de creación es obligatoria.")
        if not self.para:
            self.errores.append("El campo 'para' es obligatorio.")
        if not self.banner_producto:
            self.errores.append("El  banner del producto es obligatorio.")

        if self.errores:
            print(f"Errores de validación: {self.errores}")
            return False
        return len(self.errores) == 0
    
    @classmethod
    def colores(cls, id_producto):
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT id_color_producto, colores, cod_producto, descripcion, imagen, id_producto 
                    FROM color_producto 
                    WHERE id_producto = %s
                """
                cursor.execute(query, (id_producto,))
                resultados = cursor.fetchall()

                # Creamos una lista de objetos ColorProducto
                colores = []
                for row in resultados:
                    color = ColorProducto(
                        id_color_producto=row[0],
                        colores=row[1],
                        cod_producto=row[2],
                        descripcion=row[3],
                        imagen=row[4],
                        id_producto=row[5]
                    )
                    colores.append(color)
                return colores

        except Exception as e:
            print(f'Error al obtener colores: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)
            
            
    @classmethod
    def tallas(cls, id_color_producto):
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT id_talla_producto, talla, stock, descripcion, id_color_producto
                    FROM talla_producto
                    WHERE id_color_producto = %s
                """
                cursor.execute(query, (id_color_producto,))
                resultados = cursor.fetchall()

                # Crear lista de objetos TallaProducto
                tallas = []
                for row in resultados:
                    talla = TallaProducto(
                        id_talla_producto=row[0],
                        talla=row[1],
                        stock=row[2],
                        descripcion=row[3],
                        id_color_producto=row[4]
                    )
                    tallas.append(talla)
                return tallas

        except Exception as e:
            print(f'Error al obtener tallas: {e}')
            print(f'Error al obtener tallas: {query}, {id_color_producto}')
            return []
        finally:
            cls.liberar_conexion(conexion)
        
    @classmethod
    def productos_colores_y_tallas(cls, id_producto):
        # Obtener el producto
        producto = Producto().find(id_producto)
        sucursal = Sucursal()
        categorias = Categorias()
        cate = categorias.find(producto.id_categoria)
        ca = cate.nombre
        su= sucursal.find(producto.id_sucursal)
        imagenCategoria = cate.imagen
        if not producto:
            return None

        # Convertir producto a diccionario
        producto_dict = {
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "imagen": producto.imagen,
            "fecha_creacion": producto.fecha_creacion,
            "genero": producto.genero,
            "precio": producto.precio,
            "para": producto.para,
            "sucursal": su,
            "categoria": cate,
        }
        # Obtener colores del producto
        colores = cls.colores(id_producto)
        colores_con_tallas = []

        for color in colores:
            color_dict = {
                "id_color_producto": color.id_color_producto,
                "colores": color.colores,
                "cod_producto": color.cod_producto,
                "descripcion": color.descripcion,
                "imagen": color.imagen,
                "id_producto": color.id_producto
            }

            # Obtener tallas para cada color
            tallas = cls.tallas(color.id_color_producto)
            color_dict["tallas"] = [{
                "id_talla_producto": talla.id_talla_producto,
                "talla": talla.talla,
                "stock": talla.stock,
                "descripcion": talla.descripcion,
                "id_color_producto": talla.id_color_producto
            } for talla in tallas]

            colores_con_tallas.append(color_dict)

        producto_dict["colores"] = colores_con_tallas
        return producto_dict

        
    @classmethod
    def mostrar_productos_categoria(cls, id_categoria, pagina=1, productos_por_pagina=10):
        conexion = cls.obtener_conexion()
        try:
            offset = (pagina - 1) * productos_por_pagina
    
            with conexion.cursor() as cursor:
                query = """
                    SELECT p.id_producto, p.nombre, p.descripcion, p.imagen, p.fecha_creacion,
                           p.genero, p.precio, p.para, p.id_sucursal, p.id_categoria,
                           AVG(c.puntuacion) AS promedio_calificacion
                    FROM producto p
                    LEFT JOIN calificacion_producto c ON p.id_producto = c.id_producto
                    WHERE p.id_categoria = %s
                    GROUP BY p.id_producto
                    ORDER BY p.id_producto ASC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (id_categoria, productos_por_pagina, offset))
                resultados = cursor.fetchall()
    
                productos = []
                for row in resultados:
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        imagen=row[3],
                        fecha_creacion=row[4],
                        genero=row[5],
                        precio=row[6],
                        para=row[7],
                        id_sucursal=row[8],
                        id_categoria=row[9]
                    )
                    producto.promedio_calificacion = float(row[10]) if row[10] is not None else 0
                    productos.append(producto)
    
                return productos
    
        except Exception as e:
            print(f'Error al obtener productos por categoría: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def productos_paginados(cls, pagina, cantidad_por_pagina=6):
        conexion = cls.obtener_conexion()
        try:
            offset = (pagina - 1) * cantidad_por_pagina
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_producto, nombre, descripcion, imagen, 
                        fecha_creacion, genero, precio, para, 
                        id_sucursal, id_categoria
                    FROM producto
                    ORDER BY id_producto  DESC
                    LIMIT %s OFFSET %s;
                """, (cantidad_por_pagina, offset))

                productos = []
                for row in cursor.fetchall():
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        imagen=row[3],
                        fecha_creacion=row[4],
                        genero=row[5],
                        precio=row[6],
                        para=row[7],
                        id_sucursal=row[8],
                        id_categoria=row[9]
                    )
                    # Asignar 0.0 como valor por defecto
                    producto.promedio_calificacion = 0.0
                    productos.append(producto)

                return productos

        except Exception as e:
            print(f'Error al obtener productos paginados: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)
    
    
    @classmethod
    def mejores_calificados(cls):
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Primero intentamos obtener los mejor calificados
                query = """
                    SELECT p.id_producto, p.nombre, p.descripcion, p.imagen, p.fecha_creacion,
                           p.genero, p.precio, p.para, p.id_sucursal, p.id_categoria,
                           AVG(c.puntuacion) AS promedio_calificacion
                    FROM producto p
                    LEFT JOIN calificacion_producto c ON p.id_producto = c.id_producto
                    GROUP BY p.id_producto
                    HAVING AVG(c.puntuacion) IS NOT NULL
                    ORDER BY promedio_calificacion DESC
                    LIMIT %s
                """
                cursor.execute(query, (10,))
                resultados = cursor.fetchall()

                productos = []
                for row in resultados:
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        imagen=row[3],
                        fecha_creacion=row[4],
                        genero=row[5],
                        precio=row[6],
                        para=row[7],
                        id_sucursal=row[8],
                        id_categoria=row[9]
                    )
                    producto.promedio_calificacion = float(row[10]) if row[10] is not None else 0.0
                    productos.append(producto)

                # Si no hay productos calificados, obtenemos 10 aleatorios
                if not productos:
                    query_random = """
                        SELECT id_producto, nombre, descripcion, imagen, fecha_creacion,
                               genero, precio, para, id_sucursal, id_categoria
                        FROM producto
                        ORDER BY RANDOM()
                        LIMIT %s
                    """
                    cursor.execute(query_random, (10,))
                    resultados_random = cursor.fetchall()

                    for row in resultados_random:
                        producto = Producto(
                            id_producto=row[0],
                            nombre=row[1],
                            descripcion=row[2],
                            imagen=row[3],
                            fecha_creacion=row[4],
                            genero=row[5],
                            precio=row[6],
                            para=row[7],
                            id_sucursal=row[8],
                            id_categoria=row[9]
                        )
                        producto.promedio_calificacion = float(4.5)  # Se asegura que sea flotante
                        productos.append(producto)

                return productos

        except Exception as e:
            print(f'Error al obtener productos mejor calificados: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def mejores_calificados_paginados(cls, pagina=1, productos_por_pagina=10):
        conexion = cls.obtener_conexion()
        try:
            offset = (pagina - 1) * productos_por_pagina
            with conexion.cursor() as cursor:
                query = """
                    SELECT p.id_producto, p.nombre, p.descripcion, p.imagen, p.fecha_creacion,
                           p.genero, p.precio, p.para, p.id_sucursal, p.id_categoria,
                           AVG(c.puntuacion) AS promedio_calificacion
                    FROM producto p
                    JOIN calificacion_producto c ON p.id_producto = c.id_producto
                    GROUP BY p.id_producto
                    ORDER BY promedio_calificacion DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (productos_por_pagina, offset))
                resultados = cursor.fetchall()

                productos = []
                for row in resultados:
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        imagen=row[3],
                        fecha_creacion=row[4],
                        genero=row[5],
                        precio=row[6],
                        para=row[7],
                        id_sucursal=row[8],
                        id_categoria=row[9]
                    )
                    producto.promedio_calificacion = float(row[10]) if row[10] is not None else 0
                    productos.append(producto)

                return productos

        except Exception as e:
            print(f'Error al obtener productos mejor calificados paginados: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)
            
    @classmethod
    def productos_recientes(cls, limite=10):
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT p.id_producto, p.nombre, p.descripcion, p.imagen, p.fecha_creacion,
                           p.genero, p.precio, p.para, p.id_sucursal, p.id_categoria,
                           AVG(c.puntuacion) AS promedio_calificacion
                    FROM producto p
                    LEFT JOIN calificacion_producto c ON p.id_producto = c.id_producto
                    GROUP BY p.id_producto
                    ORDER BY p.fecha_creacion DESC
                    LIMIT %s
                """
                cursor.execute(query, (limite,))
                resultados = cursor.fetchall()

                productos = []
                for row in resultados:
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        imagen=row[3],
                        fecha_creacion=row[4],
                        genero=row[5],
                        precio=row[6],
                        para=row[7],
                        id_sucursal=row[8],
                        id_categoria=row[9]
                    )
                    producto.promedio_calificacion = float(row[10]) if row[10] is not None else 0.0
                    productos.append(producto)

                return productos

        except Exception as e:
            print(f'Error al obtener productos recientes: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)


    @classmethod
    def buscar_productos(cls, termino):
        conexion = cls.obtener_conexion()
        try:
            palabras = termino.strip().lower().split()  # Divide por espacios y pasa todo a minúsculas

            # Construir condiciones dinámicamente para cada palabra en múltiples columnas
            condiciones = " OR ".join(
                ["(LOWER(p.nombre) LIKE %s OR LOWER(p.descripcion) LIKE %s OR LOWER(p.genero) LIKE %s OR LOWER(p.para) LIKE %s)"]
                * len(palabras)
            )

            query = f"""
                SELECT p.id_producto, p.nombre, p.descripcion, p.imagen, p.fecha_creacion,
                       p.genero, p.precio, p.para, p.id_sucursal, p.id_categoria,
                       AVG(c.puntuacion) AS promedio_calificacion
                FROM producto p
                LEFT JOIN calificacion_producto c ON p.id_producto = c.id_producto
                WHERE {condiciones}
                GROUP BY p.id_producto
                ORDER BY p.fecha_creacion DESC
            """

            # Crear los parámetros para cada palabra (4 columnas por palabra)
            parametros = []
            for palabra in palabras:
                like = f"%{palabra}%"
                parametros.extend([like] * 4)

            with conexion.cursor() as cursor:
                cursor.execute(query, tuple(parametros))
                resultados = cursor.fetchall()

                productos = []
                for row in resultados:
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        imagen=row[3],
                        fecha_creacion=row[4],
                        genero=row[5],
                        precio=row[6],
                        para=row[7],
                        id_sucursal=row[8],
                        id_categoria=row[9]
                    )
                    producto.promedio_calificacion = float(row[10]) if row[10] is not None else 0.0
                    productos.append(producto)

                return productos

        except Exception as e:
            print(f'Error al buscar productos: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def obtener_similares(cls, id_producto, limite=10):
        conexion = cls.obtener_conexion()
        try:
            # Primero obtenemos el producto original
            producto_actual = cls.find(id_producto)
            if not producto_actual:
                return []

            nombre_actual = producto_actual.nombre
            id_categoria = producto_actual.id_categoria

            # Extraemos palabras clave del nombre (simples)
            palabras_clave = nombre_actual.lower().split()
            condiciones_like = " OR ".join(["p.nombre LIKE %s" for _ in palabras_clave])
            parametros_like = [f"%{palabra}%" for palabra in palabras_clave]

            with conexion.cursor() as cursor:
                query = f"""
                    SELECT p.id_producto, p.nombre, p.descripcion, p.imagen, p.fecha_creacion,
                           p.genero, p.precio, p.para, p.id_sucursal, p.id_categoria,
                           AVG(c.puntuacion) AS promedio_calificacion
                    FROM producto p
                    LEFT JOIN calificacion_producto c ON p.id_producto = c.id_producto
                    WHERE p.id_producto != %s AND (
                        p.id_categoria = %s OR {condiciones_like}
                    )
                    GROUP BY p.id_producto
                    ORDER BY p.fecha_creacion DESC
                    LIMIT %s
                """
                parametros = [id_producto, id_categoria] + parametros_like + [limite]
                cursor.execute(query, parametros)
                resultados = cursor.fetchall()

                productos_similares = []
                for row in resultados:
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        imagen=row[3],
                        fecha_creacion=row[4],
                        genero=row[5],
                        precio=row[6],
                        para=row[7],
                        id_sucursal=row[8],
                        id_categoria=row[9]
                    )
                    producto.promedio_calificacion = float(row[10]) if row[10] is not None else 0.0
                    productos_similares.append(producto)

                return productos_similares

        except Exception as e:
            print(f'Error al obtener productos similares: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def obtener_banners_aleatorios(cls, limite=3):
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT id_producto, nombre, precio, banner_producto 
                    FROM producto 
                    WHERE banner_producto IS NOT NULL
                    ORDER BY RANDOM() 
                    LIMIT %s
                """
                cursor.execute(query, (limite,))
                return cursor.fetchall()  # Devuelve lista de tuplas

        except Exception as e:
            print(f'Error al obtener banners: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def obtener_por_imagenes(cls, nombres_imagen: list[str]) -> list['Producto']:
        """
        Busca productos cuyos nombres de imagen coincidan exactamente con los proporcionados,
        incluyendo el promedio de calificación como en obtener_similares().
        
        Args:
            nombres_imagen (list[str]): Lista de nombres de imágenes (ej: ["camisa.jpg", "zapato.png"])
            
        Returns:
            list[Producto]: Lista de objetos Producto con promedio_calificacion
        """
        if not nombres_imagen:
            return []
        
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Crear placeholders para la consulta IN
                placeholders = ', '.join(['%s'] * len(nombres_imagen))
                
                query = f"""
                    SELECT p.id_producto, p.nombre, p.descripcion, p.imagen, p.fecha_creacion,
                           p.genero, p.precio, p.para, p.id_sucursal, p.id_categoria,
                           AVG(c.puntuacion) AS promedio_calificacion
                    FROM producto p
                    LEFT JOIN calificacion_producto c ON p.id_producto = c.id_producto
                    WHERE p.imagen IN ({placeholders})
                    GROUP BY p.id_producto
                    ORDER BY p.fecha_creacion DESC
                """
                
                cursor.execute(query, nombres_imagen)
                resultados = cursor.fetchall()
                
                productos = []
                for row in resultados:
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        imagen=row[3],
                        fecha_creacion=row[4],
                        genero=row[5],
                        precio=row[6],
                        para=row[7],
                        id_sucursal=row[8],
                        id_categoria=row[9]
                    )
                    producto.promedio_calificacion = float(row[10]) if row[10] is not None else 0
                    productos.append(producto)
                
                return productos
        
        except Exception as e:
            print(f'Error al buscar productos por imágenes: {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)
            
    @classmethod
    def mostrar_datos(cls,self):
        """
        Imprime todos los atributos del producto de forma legible.
        """
        print("Datos del producto:")
        for atributo in self.columnas_db:
            valor = getattr(self, atributo, None)
            print(f"{atributo}: {valor}")
            
    @classmethod
    def obtener_promedio_calificacion(cls, id_producto):
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(AVG(puntuacion), 0)
                    FROM calificacion_producto
                    WHERE id_producto = %s;
                """, (id_producto,))
                return float(cursor.fetchone()[0])
        finally:
            cls.liberar_conexion(conexion)