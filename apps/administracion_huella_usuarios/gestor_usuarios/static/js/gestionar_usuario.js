// gestionar_usuario.js

// Mostrar/ocultar formulario de creación
document.addEventListener('DOMContentLoaded', function() {
    const btnMostrar = document.getElementById('btnMostrarFormulario');
    const btnCerrar = document.getElementById('btnCerrarFormulario');
    const btnCancelar = document.getElementById('btnCancelarFormulario');
    const formulario = document.getElementById('formularioCrear');
    
    if (btnMostrar) {
        btnMostrar.addEventListener('click', function() {
            formulario.style.display = 'block';
            formulario.scrollIntoView({ behavior: 'smooth' });
        });
    }
    
    function cerrarFormulario() {
        if (formulario) {
            formulario.style.display = 'none';
            // Limpiar el formulario
            const form = document.querySelector('#formularioCrear form');
            if (form) form.reset();
            const divFicha = document.getElementById('divFicha');
            if (divFicha) divFicha.style.display = 'none';
        }
    }
    
    if (btnCerrar) btnCerrar.addEventListener('click', cerrarFormulario);
    if (btnCancelar) btnCancelar.addEventListener('click', cerrarFormulario);
    
    // Mostrar campo ficha solo cuando el rol es aprendiz
    const selectRol = document.getElementById('selectRol');
    if (selectRol) {
        selectRol.addEventListener('change', function() {
            const divFicha = document.getElementById('divFicha');
            const selectedText = this.options[this.selectedIndex]?.text.toLowerCase();
            if (divFicha) {
                divFicha.style.display = selectedText === 'aprendiz' ? 'block' : 'none';
            }
        });
    }
    
    // Mostrar/ocultar filtros de aprendiz según el rol seleccionado
    const selectRolFiltro = document.querySelector('select[name="filtro_rol"]');
    const divFiltrosAprendiz = document.getElementById('filtrosAprendiz');
    
    function toggleFiltrosAprendiz() {
        if (selectRolFiltro && divFiltrosAprendiz) {
            if (selectRolFiltro.value === 'aprendiz') {
                divFiltrosAprendiz.style.display = 'flex';
            } else {
                divFiltrosAprendiz.style.display = 'none';
            }
        }
    }
    
    if (selectRolFiltro) {
        selectRolFiltro.addEventListener('change', toggleFiltrosAprendiz);
        toggleFiltrosAprendiz();
    }
});

// Función global para editar usuario
function editarUsuario(id) {
    alert('Editar usuario ID: ' + id);
}