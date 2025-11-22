from app.classes.ColorProducto import ColorProducto
from app.classes.Activerecord import Activerecord
from decimal import Decimal
from psycopg2.extras import DictCursor

class ProductoCarrito(Activerecord):
    TABLA = 'producto_carrito'
    nombre_id = 'id_producto_carrito'
    columnas_db = [
        'id_producto_carrito',
        'fecha_anadido',
        'cantidad',
        'talla',
        'precio_unitario',
        'precio_total',
        'id_carrito',
        'id_color_producto'
    ]
    errores = []

    def __init__(
        self,
        id_producto_carrito=None,
        fecha_anadido=None,
        cantidad=None,
        talla=None,
        precio_unitario=None,
        precio_total=None,
        id_carrito=None,
        id_color_producto=None
    ):
        self.id_producto_carrito = id_producto_carrito
        self.fecha_anadido = fecha_anadido
        self.cantidad = cantidad
        self.talla = talla
        self.precio_unitario = precio_unitario
        self.precio_total = precio_total
        self.id_carrito = id_carrito
        self.id_color_producto = id_color_producto


    @classmethod
    def actualizar_o_sumar_cantidad(cls, id_carrito: int, id_color_producto: int, talla: str, cantidad_a_sumar: int) -> bool:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                # Buscar si ya existe el producto en el carrito con esa talla
                query = f"""
                    SELECT id_producto_carrito, cantidad, precio_unitario 
                    FROM {cls.TABLA} 
                    WHERE id_carrito = %s AND id_color_producto = %s AND talla = %s
                    LIMIT 1
                """
                cursor.execute(query, (id_carrito, id_color_producto, talla))
                resultado = cursor.fetchone()

                if resultado:
                    nueva_cantidad = resultado["cantidad"] + cantidad_a_sumar
                    precio_unitario = resultado["precio_unitario"]
                    nuevo_precio_total = nueva_cantidad * precio_unitario

                    update_query = f"""
                        UPDATE {cls.TABLA} 
                        SET cantidad = %s, precio_total = %s
                        WHERE id_producto_carrito = %s
                    """
                    cursor.execute(update_query, (nueva_cantidad, nuevo_precio_total, resultado["id_producto_carrito"]))
                    conexion.commit()
                    return True
                else:
                    return False  # No se encontró, podrías insertar uno nuevo luego si es necesario
        except Exception as e:
            print(f"Error en actualizar_o_sumar_cantidad: {e}")
            return False
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def obtener_productos_ultimo_carrito_pendiente(cls, id_cliente: int) -> list["ProductoCarrito"]:
        productos = []
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                # Obtener el último carrito sin importar estado
                query_ultimo_carrito = """
                    SELECT id_carrito, estado 
                    FROM carrito 
                    WHERE id_cliente = %s 
                    ORDER BY fecha_creacion DESC 
                    LIMIT 1
                """
                cursor.execute(query_ultimo_carrito, (id_cliente,))
                carrito = cursor.fetchone()

                # Si no hay carrito o el estado no es pendiente, retornar lista vacía
                if not carrito or carrito['estado'] != 'pendiente':
                    return productos

                id_carrito = carrito["id_carrito"]

                # Obtener los productos de ese carrito pendiente
                query_productos = f"""
                    SELECT {', '.join(cls.columnas_db)} 
                    FROM {cls.TABLA} 
                    WHERE id_carrito = %s
                """
                cursor.execute(query_productos, (id_carrito,))
                resultados = cursor.fetchall()

                for fila in resultados:
                    producto = cls(
                        id_producto_carrito = fila.get('id_producto_carrito'),
                        fecha_anadido = fila.get('fecha_anadido'),
                        cantidad = fila.get('cantidad'),
                        talla = fila.get('talla'),
                        precio_unitario = fila.get('precio_unitario'),
                        precio_total = fila.get('precio_total'),
                        id_carrito = fila.get('id_carrito'),
                        id_color_producto = fila.get('id_color_producto')
                    )
                    productos.append(producto)

            return productos
        except Exception as e:
            print(f"Error en obtener_productos_ultimo_carrito_pendiente: {e}")
            return []
        finally:
            cls.liberar_conexion(conexion)

    def to_dict(self):
        colorproducto = ColorProducto.buscar_descripcion_e_imagen(self.id_color_producto)
        return {
            "id_producto_carrito": self.id_producto_carrito,
            "fecha_anadido": self.fecha_anadido.isoformat() if self.fecha_anadido else None,
            "cantidad": self.cantidad,
            "talla": self.talla,
            "precio_unitario": float(self.precio_unitario) if isinstance(self.precio_unitario, Decimal) else self.precio_unitario,
            "precio_total": float(self.precio_total) if isinstance(self.precio_total, Decimal) else self.precio_total,
            "id_carrito": self.id_carrito,
            "id_color_producto": self.id_color_producto,
            "descripcion": colorproducto[0] if colorproducto else " ",
            "imagen": colorproducto[1] if colorproducto else "",
        }

    @classmethod
    def actualizar_cantidad(cls, id_producto_carrito: int, incremento_cantidad: int) -> bool:
        """
        Incrementa o decrementa la cantidad de un producto en el carrito
    
        Args:
            id_producto_carrito: ID del producto en el carrito
            incremento_cantidad: Cantidad a sumar/restar (puede ser negativo)
        
        Returns:
            bool: True si se actualizó correctamente
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                # 1. Obtener el producto actual
                producto_carrito = ProductoCarrito.find(id_producto_carrito)
                if not producto_carrito:
                    return False  # No se encontró el producto
                
                # 2. Calcular la nueva cantidad
                cantidad_final = producto_carrito.cantidad + incremento_cantidad
                
                # 3. Si la cantidad final es <= 0, eliminar el producto
                if cantidad_final <= 0:
                    return cls.borrar(id_producto_carrito)
                
                # 4. Calcular el NUEVO precio total CORRECTAMENTE
                # El precio total debe ser: cantidad_final * precio_unitario
                nuevo_precio_total = cantidad_final * producto_carrito.precio_unitario
                
                # 5. Actualizar la cantidad y el precio total
                update_query = f"""
                    UPDATE {cls.TABLA} 
                    SET cantidad = %s, precio_total = %s
                    WHERE id_producto_carrito = %s
                """
                cursor.execute(update_query, (cantidad_final, nuevo_precio_total, id_producto_carrito))
                conexion.commit()
                return True
                
        except Exception as e:
            print(f"Error en actualizar_cantidad: {e}")
            conexion.rollback()
            return False
        finally:
            cls.liberar_conexion(conexion)