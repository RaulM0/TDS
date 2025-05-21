CREATE DATABASE IF NOT EXISTS gestion_clubes;
USE gestion_clubes;

CREATE TABLE IF NOT EXISTS estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    codigo_estudiante VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    appat VARCHAR(100) NOT NULL,
    apmat VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    fecha_nacimiento DATE,
    carrera VARCHAR(100),
    semestre INT,
    estado_inscripcion ENUM('Inscrito', 'No inscrito', 'Graduado', 'Baja temporal') DEFAULT 'Inscrito',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS clubes (
    id_club INT AUTO_INCREMENT PRIMARY KEY,
    codigo_club VARCHAR(20) UNIQUE NOT NULL,
    nombre_club VARCHAR(100) NOT NULL,
    descripcion TEXT,
    responsable VARCHAR(100),
    correo_contacto VARCHAR(100),
    estado ENUM('Activo', 'Inactivo', 'En pausa') DEFAULT 'Activo',
    fecha_creacion DATE,
    max_miembros INT,
    requisitos TEXT,
    logo_path VARCHAR(255),
    fecha_creacion_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS membresias (
    id_membresia INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_club INT NOT NULL,
    fecha_inscripcion DATE NOT NULL,
    fecha_expiracion DATE,
    estado_membresia ENUM('Activa', 'Inactiva', 'Suspendida', 'En proceso') DEFAULT 'En proceso',
    rol ENUM('Miembro', 'Coordinador', 'Secretario', 'Tesorero', 'Asesor') DEFAULT 'Miembro',
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (id_club) REFERENCES clubes(id_club) ON DELETE CASCADE,
    UNIQUE KEY unique_membresia (id_estudiante, id_club)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_membresia INT NOT NULL,
    fecha_pago DATE NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago ENUM('Efectivo', 'Transferencia', 'Tarjeta', 'Beca') NOT NULL,
    referencia_pago VARCHAR(100),
    periodo_cubierto VARCHAR(50),
    estado_pago ENUM('Completo', 'Pendiente', 'Rechazado', 'Reembolsado') DEFAULT 'Pendiente',
    notas TEXT,
    FOREIGN KEY (id_membresia) REFERENCES membresias(id_membresia) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cursos (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    codigo_curso VARCHAR(20) UNIQUE NOT NULL,
    nombre_curso VARCHAR(100) NOT NULL,
    descripcion TEXT,
    creditos INT,
    departamento VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS historial_academico (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_curso INT NOT NULL,
    calificacion DECIMAL(4,2),
    fecha_inicio DATE,
    fecha_fin DATE,
    periodo VARCHAR(20),
    estado ENUM('Aprobado', 'Reprobado', 'En curso', 'Retirado') DEFAULT 'En curso',
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    rol ENUM('Administrador', 'Coordinador') DEFAULT 'Coordinador',
    estado ENUM('Activo', 'Inactivo', 'Suspendido') DEFAULT 'Activo',
    ultimo_acceso TIMESTAMP NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE INDEX idx_estudiante_nombre ON estudiantes(nombre, appat, apmat);
CREATE INDEX idx_club_nombre ON clubes(nombre_club);
CREATE INDEX idx_membresia_estado ON membresias(estado_membresia);



insert into estudiantes (codigo_estudiante, nombre, appat, apmat, correo, telefono, fecha_nacimiento, carrera, semestre, estado_inscripcion) values
('E001', 'Juan', 'Pérez', 'Gómez', 'a@gmail.com', '123456789', '2000-01-01', 'Ingeniería', 5, 'Inscrito');

INSERT INTO usuarios (
    id_estudiante,
    nombre_usuario,
    contrasena,
    correo,
    rol,
    estado,
    ultimo_acceso
) VALUES (
    1,
    'raul',
    '123', 
    'demo@ejemplo.com',
    'Coordinador',
    'Activo',
    NOW()
);
