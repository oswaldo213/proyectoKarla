CREATE TABLE Usuarios(
    Id_usuario INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Identificador VARCHAR(8) NOT NULL UNIQUE,
    Nombre VARCHAR(50) NOT NULL, 
    Apellido VARCHAR(50) NOT NULL,
    Rol VARCHAR(50) NOT NULL
    
);

CREATE TABLE Equipo(
    Id_equipo INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Identificador VARCHAR(8) NOT NULL UNIQUE,
    Nombre VARCHAR(50) NOT NULL
);

CREATE TABLE Prestamo(
    Id_Prestamo INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Id_usuario INT NOT NULL,
    Id_equipo INT NOT NULL,
    FOREIGN KEY (Id_usuario) REFERENCES Usuarios(Id_usuario),
    FOREIGN KEY (Id_equipo) REFERENCES Equipo(Id_equipo)
);

CREATE TABLE Prestamos_Detalles(
    Id_prest_Detalle INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Id_prestamo INT NOT NULL,
    Id_equipo INT NOT NULL,
    Fecha DATE NOT NULL,
    Hora TIME NOT NULL,
    FOREIGN KEY (Id_prestamo) REFERENCES Prestamo(Id_Prestamo),
    FOREIGN KEY (Id_equipo) REFERENCES Equipo(Id_equipo)
);

CREATE TABLE Peticion(
    Id_peticion INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Identificador VARCHAR(8) NOT NULL,
    FOREIGN KEY (Identificador) REFERENCES Usuarios(Identificador),
    Fecha DATE NOT NULL,
    Hora TIME NOT NULL
);

CREATE TABLE Peticiones_negadas(
    Id_peticion INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Identificador VARCHAR(8) NOT NULL,
    Fecha DATE NOT NULL,
    Hora TIME NOT NULL
);

 CREATE TABLE Sesion_activa (
    Id_usuario INT PRIMARY KEY,
    Timestamp  DATETIME NOT NULL,
    dentro     TINYINT(1) DEFAULT 0,
    FOREIGN KEY (Id_usuario) REFERENCES Usuarios(Id_usuario)
);

