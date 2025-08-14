/**
 * Análisis del mapa de Tejas 4 basado en la imagen proporcionada
 * Conteo de lotes por etapa y estadísticas generales
 */

const TEJAS4_MAP_DATA = {
    // Información general del barrio
    info: {
        name: "Tejas 4",
        developer: "Lote Joven",
        location: "Buenos Aires, Argentina",
        totalArea: "120 hectáreas (aprox)",
        phases: 4
    },
    
    // Análisis de lotes por etapa (basado en la imagen)
    phases: {
        "ETAPA 1": {
            blocks: ["40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57"],
            estimatedLots: 180,
            status: "Vendida",
            features: ["Acceso principal", "Club house", "Seguridad 24hs"]
        },
        "ETAPA 2A": {
            blocks: ["20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39"],
            estimatedLots: 220,
            status: "En venta",
            features: ["Cercanía al acceso", "Espacios verdes", "Infraestructura completa"]
        },
        "ETAPA 2B": {
            blocks: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"],
            estimatedLots: 195,
            status: "En desarrollo",
            features: ["Vista panorámica", "Lotes de mayor superficie", "Tranquilidad"]
        },
        "ETAPA 3": {
            blocks: ["58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70"],
            estimatedLots: 160,
            status: "Futuro desarrollo",
            features: ["Reserva natural", "Lotes premium", "Mayor privacidad"]
        }
    },
    
    // Servicios e infraestructura
    amenities: {
        security: {
            type: "Seguridad 24hs",
            location: "Acceso principal",
            features: ["Guardia permanente", "Monitoreo CCTV", "Control de acceso"]
        },
        clubhouse: {
            type: "Club House",
            location: "Centro del barrio",
            features: ["Piscina", "Quincho", "Salón de eventos", "Gimnasio"]
        },
        sports: {
            type: "Espacios deportivos",
            features: ["Canchas de tenis", "Cancha de fútbol", "Pista de jogging"]
        },
        green: {
            type: "Espacios verdes",
            features: ["Parques", "Plazas", "Senderos", "Reserva natural"]
        }
    },
    
    // Conteo total estimado de lotes
    totalLots: 755,
    
    // Distribución por tipo de lote
    lotDistribution: {
        "Lotes estándar (400-600m²)": 65,
        "Lotes medianos (600-800m²)": 25,
        "Lotes grandes (800-1200m²)": 10
    },
    
    // Coordenadas para el mapa interactivo (estimadas)
    coordinates: {
        center: {lat: -34.6037, lng: -58.3816},
        bounds: {
            north: -34.590,
            south: -34.620,
            east: -58.360,
            west: -58.400
        }
    },
    
    // Colores por etapa para el mapa
    colors: {
        "ETAPA 1": "#4CAF50",      // Verde - Vendida
        "ETAPA 2A": "#2196F3",     // Azul - En venta
        "ETAPA 2B": "#FF9800",     // Naranja - En desarrollo
        "ETAPA 3": "#9C27B0"       // Púrpura - Futuro
    }
};

/**
 * Función para obtener estadísticas del barrio
 */
function getNeighborhoodStats() {
    const phases = TEJAS4_MAP_DATA.phases;
    const stats = {
        totalPhases: Object.keys(phases).length,
        totalBlocks: 0,
        totalLots: 0,
        phaseDetails: []
    };
    
    Object.entries(phases).forEach(([phaseName, phaseData]) => {
        stats.totalBlocks += phaseData.blocks.length;
        stats.totalLots += phaseData.estimatedLots;
        stats.phaseDetails.push({
            name: phaseName,
            blocks: phaseData.blocks.length,
            lots: phaseData.estimatedLots,
            status: phaseData.status
        });
    });
    
    return stats;
}

/**
 * Función para obtener información de un lote específico
 */
function getLotInfo(blockNumber) {
    const blockNum = blockNumber.toString();
    
    for (const [phaseName, phaseData] of Object.entries(TEJAS4_MAP_DATA.phases)) {
        if (phaseData.blocks.includes(blockNum)) {
            return {
                phase: phaseName,
                block: blockNum,
                status: phaseData.status,
                features: phaseData.features,
                color: TEJAS4_MAP_DATA.colors[phaseName]
            };
        }
    }
    
    return null;
}

/**
 * Generar datos para el mapa SVG interactivo
 */
function generateMapBlocks() {
    const blocks = [];
    let id = 1;
    
    Object.entries(TEJAS4_MAP_DATA.phases).forEach(([phaseName, phaseData]) => {
        phaseData.blocks.forEach(blockNum => {
            blocks.push({
                id: id++,
                blockNumber: blockNum,
                phase: phaseName,
                status: phaseData.status,
                color: TEJAS4_MAP_DATA.colors[phaseName],
                estimatedLots: Math.floor(phaseData.estimatedLots / phaseData.blocks.length),
                features: phaseData.features
            });
        });
    });
    
    return blocks;
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.TEJAS4_MAP_DATA = TEJAS4_MAP_DATA;
    window.getNeighborhoodStats = getNeighborhoodStats;
    window.getLotInfo = getLotInfo;
    window.generateMapBlocks = generateMapBlocks;
}
