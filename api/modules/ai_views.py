from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

DIAGNOSIS_DB = {
    "P0300": {
        "title": "Misfire Detected - Multi-Cylinder Analysis",
        "details": [
            "Inspect and replace worn spark plugs (est. 0.5 hrs)",
            "Check ignition coils for proper resistance values",
            "Test fuel injectors for clogging or leak patterns",
            "Verify compression across all cylinders"
        ],
        "severity": "High",
        "estimated_cost": "MWK 15,000 - 45,000"
    },
    "P0420": {
        "title": "Catalyst Efficiency Below Threshold",
        "details": [
            "Inspect oxygen sensors for voltage fluctuations",
            "Check for exhaust leaks before catalytic converter",
            "Perform backpressure test on catalytic converter",
            "Replace catalytic converter if ceramic substrate is damaged (est. 2-3 hrs)"
        ],
        "severity": "Medium",
        "estimated_cost": "MWK 80,000 - 250,000"
    },
    "P0171": {
        "title": "Fuel System Too Lean - Bank 1",
        "details": [
            "Inspect mass airflow sensor for contamination",
            "Check for vacuum leaks in intake manifold gaskets",
            "Test fuel pressure regulator and pump output",
            "Clean or replace fuel injectors if spray pattern is poor"
        ],
        "severity": "Medium",
        "estimated_cost": "MWK 10,000 - 60,000"
    },
    "P0455": {
        "title": "EVAP System Leak Detected",
        "details": [
            "Inspect fuel cap seal and replace if cracked",
            "Smoke test the EVAP system to locate leak point",
            "Check charcoal canister for fuel saturation",
            "Replace EVAP purge valve if stuck open"
        ],
        "severity": "Low",
        "estimated_cost": "MWK 5,000 - 30,000"
    },
    "P0500": {
        "title": "Vehicle Speed Sensor Circuit",
        "details": [
            "Inspect VSS wiring harness for breaks or corrosion",
            "Test speed sensor output with multimeter",
            "Check instrument cluster for proper speedometer function",
            "Replace vehicle speed sensor if signal is erratic"
        ],
        "severity": "Medium",
        "estimated_cost": "MWK 8,000 - 25,000"
    },
    "P0601": {
        "title": "ECM Internal Memory Error",
        "details": [
            "Attempt ECM software reflash with latest firmware",
            "Check battery voltage and charging system stability",
            "Inspect ECM ground connections for corrosion",
            "Replace ECM if internal memory failure confirmed (est. 1-2 hrs)"
        ],
        "severity": "Critical",
        "estimated_cost": "MWK 50,000 - 200,000"
    },
    "P0700": {
        "title": "Transmission Control System Fault",
        "details": [
            "Scan TCM for additional transmission-specific codes",
            "Check transmission fluid level, color, and odor",
            "Inspect shift solenoids for electrical resistance",
            "Perform transmission line pressure test before disassembly"
        ],
        "severity": "Critical",
        "estimated_cost": "MWK 30,000 - 350,000"
    }
}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_diagnose(request):
    code = request.data.get('code', '').upper().strip()
    vehicle = request.data.get('vehicle', '').strip()
    
    if not code:
        return Response({'error': 'Fault code required'}, status=400)
    
    # Check local database first
    if code in DIAGNOSIS_DB:
        result = DIAGNOSIS_DB[code]
        result['code'] = code
        result['vehicle'] = vehicle or 'Not specified'
        result['source'] = 'local'
        return Response(result)
    
    # Generic response for unknown codes
    return Response({
        'code': code,
        'vehicle': vehicle or 'Not specified',
        'title': f'General Diagnostic for {code}',
        'details': [
            'Connect professional OBD-II scanner for live data',
            'Check related wiring harness and electrical connectors',
            'Inspect relevant sensors and actuators for affected system',
            'Clear codes, perform drive cycle, and re-scan to confirm fix'
        ],
        'severity': 'Unknown',
        'estimated_cost': 'Requires inspection',
        'source': 'local'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_codes_list(request):
    """Return list of all supported fault codes"""
    codes = []
    for code, data in DIAGNOSIS_DB.items():
        codes.append({
            'code': code,
            'title': data['title'],
            'severity': data['severity']
        })
    return Response({'supported_codes': codes, 'total': len(codes)})
