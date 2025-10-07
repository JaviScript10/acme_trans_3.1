# flota/management/commands/poblar_acme_trans.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from flota.models import CentroOperacional, Vehiculo, TipoMantenimiento, Proveedor
from datetime import date


class Command(BaseCommand):
    help = 'Pobla la base de datos con los datos iniciales de ACME Trans'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n🚀 Iniciando población de ACME Trans...\n'))
        
        # 1. Crear Centros Operacionales
        self.stdout.write('📍 Creando Centros Operacionales...')
        centros = self.crear_centros()
        
        # 2. Crear Usuarios y Roles
        self.stdout.write('\n👥 Creando Usuarios...')
        usuarios = self.crear_usuarios()
        
        # 3. Crear los 29 Vehículos
        self.stdout.write('\n🚛 Creando 29 Vehículos de la Flota...')
        self.crear_vehiculos(centros)
        
        # 4. Crear Tipos de Mantenimiento
        self.stdout.write('\n🔧 Creando Tipos de Mantenimiento...')
        self.crear_tipos_mantenimiento()
        
        # 5. Crear Proveedores
        self.stdout.write('\n🏢 Creando Proveedores...')
        self.crear_proveedores()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ ¡Población completada exitosamente!\n'))
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN:'))
        self.stdout.write(f'  • Centros: {CentroOperacional.objects.count()}')
        self.stdout.write(f'  • Vehículos: {Vehiculo.objects.count()}')
        self.stdout.write(f'  • Usuarios: {User.objects.count()}')
        self.stdout.write(f'  • Tipos Mantenimiento: {TipoMantenimiento.objects.count()}')
        self.stdout.write(f'  • Proveedores: {Proveedor.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n🔐 CREDENCIALES DE ACCESO:'))
        self.stdout.write('  • javier_dev / 12345678 (SUPERADMIN - Acceso Total)')
        self.stdout.write('  • pedro_rojas / 12345678 (Operaciones)')
        self.stdout.write('  • marcos_rojas / 12345678 (Director)')
        self.stdout.write('  • luisa_rojas / 12345678 (Finanzas)')
        self.stdout.write('  • admin_sra / 12345678 (Administración)')
        self.stdout.write(self.style.SUCCESS('\n' + '='*60 + '\n'))

    def crear_centros(self):
        """Crea los 3 centros operacionales"""
        centros_data = [
            {
                'nombre': 'Santiago',
                'direccion': 'Av. Libertador Bernardo O\'Higgins 1234',
                'ciudad': 'Santiago',
                'telefono': '+56 2 2345 6789',
                'responsable': 'Pedro Rojas',
                'capacidad_maxima': 20
            },
            {
                'nombre': 'Osorno',
                'direccion': 'Ruta 5 Sur Km 912',
                'ciudad': 'Osorno',
                'telefono': '+56 64 223 4567',
                'responsable': 'Carlos Muñoz',
                'capacidad_maxima': 15
            },
            {
                'nombre': 'Coquimbo',
                'direccion': 'Av. Costanera 567',
                'ciudad': 'Coquimbo',
                'telefono': '+56 51 234 5678',
                'responsable': 'Ana Torres',
                'capacidad_maxima': 12
            }
        ]
        
        centros = {}
        for data in centros_data:
            centro, created = CentroOperacional.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            centros[data['nombre']] = centro
            status = '✅ Creado' if created else '⚠️  Ya existe'
            self.stdout.write(f'  {status}: Centro {data["nombre"]}')
        
        return centros

    def crear_usuarios(self):
        """Crea los 5 usuarios del sistema con sus roles"""
        
        # Crear grupos/roles
        grupos = {}
        roles_data = ['Superadmin', 'Director', 'Operaciones', 'Finanzas', 'Administracion']
        
        for nombre_grupo in roles_data:
            grupo, created = Group.objects.get_or_create(name=nombre_grupo)
            grupos[nombre_grupo] = grupo
        
        # Crear usuarios
        usuarios_data = [
            {
                'username': 'javier_dev',
                'password': '12345678',
                'email': 'javier.ruiz@acmetrans.cl',
                'first_name': 'Javier',
                'last_name': 'Ruiz',
                'is_staff': True,
                'is_superuser': True,
                'grupo': 'Superadmin'
            },
            {
                'username': 'pedro_rojas',
                'password': '12345678',
                'email': 'pedro.rojas@acmetrans.cl',
                'first_name': 'Pedro',
                'last_name': 'Rojas',
                'is_staff': True,
                'is_superuser': False,
                'grupo': 'Operaciones'
            },
            {
                'username': 'marcos_rojas',
                'password': '12345678',
                'email': 'marcos.rojas@acmetrans.cl',
                'first_name': 'Marcos',
                'last_name': 'Rojas',
                'is_staff': True,
                'is_superuser': False,
                'grupo': 'Director'
            },
            {
                'username': 'luisa_rojas',
                'password': '12345678',
                'email': 'luisa.rojas@acmetrans.cl',
                'first_name': 'Luisa',
                'last_name': 'Rojas',
                'is_staff': True,
                'is_superuser': False,
                'grupo': 'Finanzas'
            },
            {
                'username': 'admin_sra',
                'password': '12345678',
                'email': 'admin@acmetrans.cl',
                'first_name': 'Administradora',
                'last_name': 'Rojas',
                'is_staff': True,
                'is_superuser': False,
                'grupo': 'Administracion'
            }
        ]
        
        usuarios = {}
        for data in usuarios_data:
            grupo_nombre = data.pop('grupo')
            username = data['username']
            
            if User.objects.filter(username=username).exists():
                usuario = User.objects.get(username=username)
                self.stdout.write(f'  ⚠️  Ya existe: {username}')
            else:
                usuario = User.objects.create_user(**data)
                usuario.groups.add(grupos[grupo_nombre])
                self.stdout.write(f'  ✅ Creado: {username} ({grupo_nombre})')
            
            usuarios[username] = usuario
        
        return usuarios

    def crear_vehiculos(self, centros):
        """Crea los 29 vehículos de ACME Trans"""
        
        # Santiago: 13 vehículos (5 GC + 8 MC)
        vehiculos_santiago = [
            {'patente': 'AB-1234', 'marca': 'Mercedes-Benz', 'modelo': 'Actros 2644', 'año': 2020, 'tipo': 'GC', 'km': 145000, 'estado': 'operativo'},
            {'patente': 'CD-5678', 'marca': 'Volvo', 'modelo': 'FH540', 'año': 2019, 'tipo': 'GC', 'km': 198000, 'estado': 'operativo'},
            {'patente': 'EF-9012', 'marca': 'Scania', 'modelo': 'R450', 'año': 2021, 'tipo': 'GC', 'km': 167000, 'estado': 'mantenimiento'},
            {'patente': 'GH-3456', 'marca': 'MAN', 'modelo': 'TGX 540', 'año': 2018, 'tipo': 'GC', 'km': 203000, 'estado': 'operativo'},
            {'patente': 'IJ-7890', 'marca': 'Iveco', 'modelo': 'Stralis 500', 'año': 2020, 'tipo': 'GC', 'km': 156000, 'estado': 'operativo'},
            {'patente': 'KL-2345', 'marca': 'Mercedes-Benz', 'modelo': 'Atego 1726', 'año': 2020, 'tipo': 'MC', 'km': 89000, 'estado': 'operativo'},
            {'patente': 'MN-6789', 'marca': 'Volvo', 'modelo': 'VM260', 'año': 2021, 'tipo': 'MC', 'km': 134000, 'estado': 'operativo'},
            {'patente': 'OP-4567', 'marca': 'Ford', 'modelo': 'Cargo 1722', 'año': 2019, 'tipo': 'MC', 'km': 97000, 'estado': 'operativo'},
            {'patente': 'QR-8901', 'marca': 'Chevrolet', 'modelo': 'NPR 816', 'año': 2020, 'tipo': 'MC', 'km': 76000, 'estado': 'operativo'},
            {'patente': 'ST-2348', 'marca': 'Hyundai', 'modelo': 'HD78', 'año': 2019, 'tipo': 'MC', 'km': 112000, 'estado': 'mantenimiento'},
            {'patente': 'UV-6792', 'marca': 'Isuzu', 'modelo': 'NQR', 'año': 2021, 'tipo': 'MC', 'km': 58000, 'estado': 'operativo'},
            {'patente': 'WX-5913', 'marca': 'JAC', 'modelo': 'HFC1061', 'año': 2020, 'tipo': 'MC', 'km': 82000, 'estado': 'operativo'},
            {'patente': 'YZ-3684', 'marca': 'Foton', 'modelo': 'Aumark', 'año': 2021, 'tipo': 'MC', 'km': 64000, 'estado': 'operativo'},
        ]
        
        # Osorno: 9 vehículos (3 GC + 6 MC)
        vehiculos_osorno = [
            {'patente': 'AA-1111', 'marca': 'Volvo', 'modelo': 'FH460', 'año': 2020, 'tipo': 'GC', 'km': 234000, 'estado': 'operativo'},
            {'patente': 'BB-2222', 'marca': 'Scania', 'modelo': 'G450', 'año': 2019, 'tipo': 'GC', 'km': 189000, 'estado': 'operativo'},
            {'patente': 'CC-3333', 'marca': 'Mercedes-Benz', 'modelo': 'Actros 2542', 'año': 2021, 'tipo': 'GC', 'km': 178000, 'estado': 'operativo'},
            {'patente': 'DD-4444', 'marca': 'Ford', 'modelo': 'Cargo 1519', 'año': 2019, 'tipo': 'MC', 'km': 145000, 'estado': 'operativo'},
            {'patente': 'EE-5555', 'marca': 'Mercedes-Benz', 'modelo': 'Accelo 1016', 'año': 2020, 'tipo': 'MC', 'km': 98000, 'estado': 'operativo'},
            {'patente': 'FF-6666', 'marca': 'Volvo', 'modelo': 'VM220', 'año': 2019, 'tipo': 'MC', 'km': 167000, 'estado': 'operativo'},
            {'patente': 'GG-7777', 'marca': 'Isuzu', 'modelo': 'NPR71', 'año': 2021, 'tipo': 'MC', 'km': 89000, 'estado': 'operativo'},
            {'patente': 'HH-8888', 'marca': 'Hyundai', 'modelo': 'HD65', 'año': 2020, 'tipo': 'MC', 'km': 124000, 'estado': 'operativo'},
            {'patente': 'II-9999', 'marca': 'JAC', 'modelo': 'N56', 'año': 2019, 'tipo': 'MC', 'km': 73000, 'estado': 'operativo'},
        ]
        
        # Coquimbo: 7 vehículos (3 GC + 4 MC)
        vehiculos_coquimbo = [
            {'patente': 'JJ-1010', 'marca': 'MAN', 'modelo': 'TGS 440', 'año': 2020, 'tipo': 'GC', 'km': 156000, 'estado': 'operativo'},
            {'patente': 'KK-2020', 'marca': 'Iveco', 'modelo': 'Trakker 500', 'año': 2019, 'tipo': 'GC', 'km': 189000, 'estado': 'operativo'},
            {'patente': 'LL-3030', 'marca': 'Scania', 'modelo': 'P450', 'año': 2021, 'tipo': 'GC', 'km': 278000, 'estado': 'fuera_servicio'},
            {'patente': 'MM-4040', 'marca': 'Ford', 'modelo': 'Cargo 815', 'año': 2019, 'tipo': 'MC', 'km': 67000, 'estado': 'operativo'},
            {'patente': 'NN-5050', 'marca': 'Chevrolet', 'modelo': 'NPR 75L', 'año': 2020, 'tipo': 'MC', 'km': 98000, 'estado': 'operativo'},
            {'patente': 'OO-6060', 'marca': 'Hyundai', 'modelo': 'HD72', 'año': 2021, 'tipo': 'MC', 'km': 45000, 'estado': 'operativo'},
            {'patente': 'PP-7070', 'marca': 'Isuzu', 'modelo': 'ELF 400', 'año': 2020, 'tipo': 'MC', 'km': 112000, 'estado': 'operativo'},
        ]
        
        # Procesar todos los vehículos
        todas_flotas = [
            ('Santiago', vehiculos_santiago),
            ('Osorno', vehiculos_osorno),
            ('Coquimbo', vehiculos_coquimbo)
        ]
        
        contador = 0
        for centro_nombre, flota in todas_flotas:
            centro = centros[centro_nombre]
            for data in flota:
                vehiculo, created = Vehiculo.objects.get_or_create(
                    patente=data['patente'],
                    defaults={
                        'marca': data['marca'],
                        'modelo': data['modelo'],
                        'año': data['año'],
                        'tipo_capacidad': data['tipo'],
                        'kilometraje_actual': data['km'],
                        'estado': data['estado'],
                        'centro_operacion': centro,
                        'fecha_adquisicion': date(data['año'], 1, 1),
                        'valor_adquisicion': 25000000 if data['tipo'] == 'GC' else 15000000,
                        'numero_chasis': f'CHASIS-{data["patente"]}',
                        'numero_motor': f'MOTOR-{data["patente"]}',
                    }
                )
                contador += 1
                status = '✅' if created else '⚠️'
                self.stdout.write(f'  {status} {data["patente"]} - {data["marca"]} {data["modelo"]} ({centro_nombre})')
        
        self.stdout.write(f'\n  📊 Total vehículos: {contador}/29')

    def crear_tipos_mantenimiento(self):
        """Crea los tipos de mantenimiento estándar"""
        tipos = [
            {
                'nombre': 'Mantenimiento Preventivo 10.000 km',
                'descripcion': 'Revisión general cada 10,000 kilómetros',
                'frecuencia_km': 10000,
                'costo_estimado': 450000,
                'tiempo_estimado_horas': 4,
                'es_preventivo': True
            },
            {
                'nombre': 'Cambio de Aceite y Filtros',
                'descripcion': 'Cambio de aceite de motor y filtros',
                'frecuencia_km': 10000,
                'costo_estimado': 180000,
                'tiempo_estimado_horas': 2,
                'es_preventivo': True
            },
            {
                'nombre': 'Revisión de Frenos',
                'descripcion': 'Inspección y mantenimiento sistema de frenos',
                'frecuencia_km': 20000,
                'costo_estimado': 350000,
                'tiempo_estimado_horas': 3,
                'es_preventivo': True
            },
            {
                'nombre': 'Reparación Sistema Eléctrico',
                'descripcion': 'Diagnóstico y reparación de fallas eléctricas',
                'frecuencia_km': 0,
                'costo_estimado': 500000,
                'tiempo_estimado_horas': 6,
                'es_preventivo': False
            },
        ]
        
        for data in tipos:
            tipo, created = TipoMantenimiento.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            status = '✅ Creado' if created else '⚠️  Ya existe'
            self.stdout.write(f'  {status}: {data["nombre"]}')

    def crear_proveedores(self):
        """Crea proveedores de mantenimiento"""
        proveedores = [
            {
                'nombre': 'Taller Central Santiago',
                'rut': '76.123.456-7',
                'direccion': 'Av. Matta 1234, Santiago',
                'telefono': '+56 2 2567 8901',
                'email': 'contacto@tallercentral.cl',
                'contacto_principal': 'Juan Pérez',
                'especialidad': 'Mantenimiento Preventivo'
            },
            {
                'nombre': 'Servicio Técnico Osorno',
                'rut': '76.234.567-8',
                'direccion': 'Ruta 5 Sur Km 915, Osorno',
                'telefono': '+56 64 234 5678',
                'email': 'servicios@tecnicoosorno.cl',
                'contacto_principal': 'María González',
                'especialidad': 'Reparaciones Generales'
            },
            {
                'nombre': 'Mantención Norte Coquimbo',
                'rut': '76.345.678-9',
                'direccion': 'Av. La Marina 890, Coquimbo',
                'telefono': '+56 51 245 6789',
                'email': 'info@mantencionnorte.cl',
                'contacto_principal': 'Carlos Ramírez',
                'especialidad': 'Sistemas Eléctricos'
            },
        ]
        
        for data in proveedores:
            proveedor, created = Proveedor.objects.get_or_create(
                rut=data['rut'],
                defaults=data
            )
            status = '✅ Creado' if created else '⚠️  Ya existe'
            self.stdout.write(f'  {status}: {data["nombre"]}')