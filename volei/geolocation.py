import streamlit as st
import streamlit.components.v1 as components

# Cria um componente customizado para capturar geolocalização
_GEOLOCATION_COMPONENT = """
<html>
<head>
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const data = {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            timestamp: new Date().toISOString()
                        };
                        window.parent.postMessage(data, "*");
                    },
                    function(error) {
                        const errorData = {
                            error: error.message,
                            code: error.code
                        };
                        window.parent.postMessage(errorData, "*");
                    }
                );
            } else {
                window.parent.postMessage({error: "Geolocalização não suportada"}, "*");
            }
        }
        
        // Executa automaticamente quando o componente carrega
        window.addEventListener('load', function() {
            setTimeout(getLocation, 100);
        });
    </script>
</head>
<body>
    <div id="status" style="text-align: center; padding: 20px; font-size: 18px; font-weight: bold;">
        📍 Obtendo sua localização...
    </div>
</body>
</html>
"""

def get_geolocation():
    """
    Retorna um componente que captura a geolocalização do usuário
    """
    return components.html(_GEOLOCATION_COMPONENT, height=100)
