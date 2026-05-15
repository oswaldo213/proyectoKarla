async function cargarAccesos() {

    const respuesta = await fetch("/api/accesos")

    const datos = await respuesta.json();
    
    const contenedor = 
    document.getElementById("contenedor-accesos");

    contenedor.innerHTML = ""; //vacio por si hay una nueva llamada

    datos.forEach(usuario => { //para cada elemento que se llama contenedor accesos
        //me vas a dar el conetido html que tenga le vas agregar esto que tengo aca

        contenedor.innerHTML += `

            <div class="cuadros-info">

                <span>Imagen</span>

                <span class="Nombre">
                    ${usuario.nombre}
                </span>

                <span id="rol">
                    ${usuario.rol}
                </span>

            </div>

        `;

    });

}

async function cargarEquipos() {

    const respuesta = await fetch("/api/Prestamos")

    const datos = await respuesta.json();
    
    const contenedor = 
    document.getElementById("contenedor-equipos");

    contenedor.innerHTML = ""; //vacio por si hay una nueva llamada

    datos.forEach(equipo => { //para cada elemento que se llama contenedor accesos
        //me vas a dar el conetido html que tenga le vas agregar esto que tengo aca

        contenedor.innerHTML += `

            <div class="cuadros-info">

                <span>Imagen</span>

                <span class="Nombre">
                    ${equipo.nombre}
                </span>

                <span class="Usuario">
                    ${equipo.usuario}
                </span>

                <span id="Fecha">
                    ${equipo.Fecha}
                </span>

                <span id="Hora">
                    ${equipo.Hora}
                </span>

            </div>

        `;

    });

}

async function cargarNegaciones() {

    const respuesta = await fetch("/api/Denegadas")

    const datos = await respuesta.json();
    
    const contenedor = 
    document.getElementById("contenedor-denegados");

    contenedor.innerHTML = ""; //vacio por si hay una nueva llamada

    datos.forEach(negacion => { //para cada elemento que se llama contenedor accesos
        //me vas a dar el conetido html que tenga le vas agregar esto que tengo aca

        contenedor.innerHTML += `

            <div class="cuadros-info">

                <span>Imagen</span>

                <span class="Nombre">
                    ${negacion.identificador}
                </span>

                <span id="Fecha">
                    ${negacion.Fecha}
                </span>

                <span id="Hora">
                    ${negacion.Hora}
                </span>

            </div>

        `;

    });

}


cargarAccesos();
cargarEquipos();
 cargarNegaciones()