import io
import base64
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from api.models import *
from api.views import get_user_garage

def get_garage_data(user):
    garage = get_user_garage(user)
    if not garage and not user.is_superuser:
        return None
    return garage

def svg_to_base64(svg_string):
    return base64.b64encode(svg_string.encode()).decode()

# === PURE SVG CHART GENERATORS (Zero Dependencies) ===

def bar_chart_svg(data, width=600, height=300):
    """Generate SVG bar chart from {label: value} dict"""
    if not data:
        return '<svg width="600" height="300"><text x="300" y="150" text-anchor="middle" fill="#888">No data</text></svg>'
    
    labels = list(data.keys())
    values = list(data.values())
    max_val = max(values) if values else 1
    colors = ['#FF6F00', '#3B82F6', '#22C55E', '#8B5CF6', '#F59E0B', '#EF4444']
    
    bar_w = (width - 80) / len(labels) - 15
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<rect width="{width}" height="{height}" fill="#1A1A1A"/>'
    svg += f'<text x="{width/2}" y="25" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="bold">Revenue by Payment Method</text>'
    
    for i, (label, val) in enumerate(zip(labels, values)):
        x = 50 + i * (bar_w + 15)
        bar_h = (val / max_val) * (height - 100)
        y = height - 40 - bar_h
        color = colors[i % len(colors)]
        
        svg += f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{color}"/>'
        svg += f'<text x="{x + bar_w/2}" y="{y - 8}" text-anchor="middle" fill="#E0E0E0" font-size="11">MWK {val:,.0f}</text>'
        svg += f'<text x="{x + bar_w/2}" y="{height - 15}" text-anchor="middle" fill="#888" font-size="10">{label}</text>'
    
    svg += '</svg>'
    return svg


def donut_chart_svg(data, width=400, height=400):
    """Generate SVG donut chart from {label: value} dict"""
    if not data:
        return '<svg width="400" height="400"><text x="200" y="200" text-anchor="middle" fill="#888">No data</text></svg>'
    
    labels = list(data.keys())
    values = list(data.values())
    total = sum(values) or 1
    colors = ['#FF6F00', '#F59E0B', '#3B82F6', '#22C55E']
    
    cx, cy, r = width/2, height/2 - 10, 120
    inner_r = 60
    
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<rect width="{width}" height="{height}" fill="#1A1A1A"/>'
    svg += f'<text x="{cx}" y="25" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="bold">Job Status Distribution</text>'
    svg += f'<text x="{cx}" y="{cy}" text-anchor="middle" fill="#E0E0E0" font-size="24" font-weight="bold">{total}</text>'
    svg += f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" fill="#888" font-size="11">Total Jobs</text>'
    
    start_angle = -90
    for i, (label, val) in enumerate(zip(labels, values)):
        angle = (val / total) * 360
        end_angle = start_angle + angle
        
        # Calculate arc path
        import math
        x1 = cx + r * math.cos(math.radians(start_angle))
        y1 = cy + r * math.sin(math.radians(start_angle))
        x2 = cx + r * math.cos(math.radians(end_angle))
        y2 = cy + r * math.sin(math.radians(end_angle))
        ix1 = cx + inner_r * math.cos(math.radians(start_angle))
        iy1 = cy + inner_r * math.sin(math.radians(start_angle))
        ix2 = cx + inner_r * math.cos(math.radians(end_angle))
        iy2 = cy + inner_r * math.sin(math.radians(end_angle))
        
        large_arc = 1 if angle > 180 else 0
        color = colors[i % len(colors)]
        
        path = f'M {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} L {ix2} {iy2} A {inner_r} {inner_r} 0 {large_arc} 0 {ix1} {iy1} Z'
        svg += f'<path d="{path}" fill="{color}"/>'
        
        # Label
        mid_angle = math.radians(start_angle + angle/2)
        lx = cx + (r + 30) * math.cos(mid_angle)
        ly = cy + (r + 30) * math.sin(mid_angle)
        pct = round((val/total)*100)
        svg += f'<text x="{lx}" y="{ly}" text-anchor="middle" fill="#888" font-size="10">{label} ({pct}%)</text>'
        
        start_angle = end_angle
    
    svg += '</svg>'
    return svg


def line_chart_svg(data, width=600, height=300):
    """Generate SVG line chart from [(label, value), ...] list"""
    if not data:
        return '<svg width="600" height="300"><text x="300" y="150" text-anchor="middle" fill="#888">No data</text></svg>'
    
    labels = [x[0] for x in data]
    values = [x[1] for x in data]
    max_val = max(values) if values else 1
    
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<rect width="{width}" height="{height}" fill="#1A1A1A"/>'
    svg += f'<text x="{width/2}" y="25" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="bold">Most Common Repairs</text>'
    
    # Grid lines
    for i in range(5):
        y = 50 + i * 45
        svg += f'<line x1="50" y1="{y}" x2="{width-30}" y2="{y}" stroke="#2A2A2A" stroke-width="1"/>'
    
    # Line and points
    points = []
    for i, val in enumerate(values):
        x = 50 + i * ((width - 80) / max(len(values)-1, 1))
        y = 50 + 200 - (val / max_val) * 180
        points.append(f'{x},{y}')
    
    if len(points) > 1:
        svg += f'<polyline points="{" ".join(points)}" fill="none" stroke="#FF6F00" stroke-width="3"/>'
        # Fill area
        first_x = 50
        last_x = 50 + (len(values)-1) * ((width - 80) / max(len(values)-1, 1))
        svg += f'<polygon points="{first_x},250 {" ".join(points)} {last_x},250" fill="rgba(255,111,0,0.1)"/>'
    
    for i, (x, y) in enumerate([(50 + i * ((width - 80) / max(len(values)-1, 1)), 50 + 200 - (val / max_val) * 180) for i, val in enumerate(values)]):
        svg += f'<circle cx="{x}" cy="{y}" r="5" fill="#FF6F00"/>'
        svg += f'<text x="{x}" y="{y - 12}" text-anchor="middle" fill="#E0E0E0" font-size="10">{val}</text>'
        svg += f'<text x="{x}" y="270" text-anchor="middle" fill="#888" font-size="9" transform="rotate(-25,{x},270)">{labels[i][:15]}</text>'
    
    svg += '</svg>'
    return svg


def polar_chart_svg(data, width=400, height=400):
    """Generate SVG polar-style chart (simplified as horizontal bars) from [(label, value), ...]"""
    if not data:
        return '<svg width="400" height="400"><text x="200" y="200" text-anchor="middle" fill="#888">No data</text></svg>'
    
    labels = [x[0] for x in data]
    values = [x[1] for x in data]
    max_val = max(values) if values else 1
    colors = ['#FF6F00', '#3B82F6', '#22C55E', '#8B5CF6', '#F59E0B', '#EF4444', '#EC4899', '#14B8A6']
    
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<rect width="{width}" height="{height}" fill="#1A1A1A"/>'
    svg += f'<text x="{width/2}" y="25" text-anchor="middle" fill="#E0E0E0" font-size="14" font-weight="bold">Jobs per Mechanic</text>'
    
    for i, (label, val) in enumerate(zip(labels, values)):
        y = 50 + i * 38
        bar_w = (val / max_val) * (width - 200)
        color = colors[i % len(colors)]
        
        svg += f'<text x="15" y="{y + 18}" fill="#888" font-size="10" text-anchor="end" width="100">{label[:18]}</text>'
        svg += f'<rect x="105" y="{y + 6}" width="{bar_w}" height="24" rx="6" fill="{color}"/>'
        svg += f'<text x="{115 + bar_w}" y="{y + 22}" fill="#E0E0E0" font-size="11" font-weight="bold">{val} jobs</text>'
    
    svg += '</svg>'
    return svg


# === API VIEWS ===

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue_chart(request):
    garage = get_garage_data(request.user)
    if not garage:
        return JsonResponse({'error': 'No garage'}, status=403)
    
    payments = Payment.objects.filter(work_order__garage=garage) if garage else Payment.objects.all()
    methods = {}
    for p in payments:
        m = p.payment_method or 'Other'
        methods[m] = methods.get(m, 0) + float(p.amount)
    
    svg = bar_chart_svg(methods)
    return JsonResponse({'chart': svg_to_base64(svg)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def status_chart(request):
    garage = get_garage_data(request.user)
    if not garage:
        return JsonResponse({'error': 'No garage'}, status=403)
    
    orders = WorkOrder.objects.filter(garage=garage) if garage else WorkOrder.objects.all()
    statuses = {'In Progress': 0, 'Awaiting Parts': 0, 'Ready (Pending Invoice)': 0, 'Completed': 0}
    for o in orders:
        if o.status in statuses:
            statuses[o.status] += 1
    
    svg = donut_chart_svg(statuses)
    return JsonResponse({'chart': svg_to_base64(svg)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def repairs_chart(request):
    garage = get_garage_data(request.user)
    if not garage:
        return JsonResponse({'error': 'No garage'}, status=403)
    
    orders = WorkOrder.objects.filter(garage=garage) if garage else WorkOrder.objects.all()
    issues = {}
    for o in orders:
        words = (o.issue_description or 'General').split()[:3]
        key = ' '.join(words)
        issues[key] = issues.get(key, 0) + 1
    
    top = sorted(issues.items(), key=lambda x: x[1], reverse=True)[:6]
    svg = line_chart_svg(top)
    return JsonResponse({'chart': svg_to_base64(svg)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mechanics_chart(request):
    garage = get_garage_data(request.user)
    if not garage:
        return JsonResponse({'error': 'No garage'}, status=403)
    
    mechs = MechanicProfile.objects.filter(garage=garage) if garage else MechanicProfile.objects.all()
    orders = WorkOrder.objects.filter(garage=garage) if garage else WorkOrder.objects.all()
    
    mech_data = []
    for m in mechs[:8]:
        count = orders.filter(mechanic=m.user).count()
        name = m.user.get_full_name() or m.user.username
        mech_data.append((name, count or 1))
    
    svg = polar_chart_svg(mech_data)
    return JsonResponse({'chart': svg_to_base64(svg)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_charts(request):
    garage = get_garage_data(request.user)
    if not garage:
        return JsonResponse({'error': 'No garage'}, status=403)
    
    payments = Payment.objects.filter(work_order__garage=garage) if garage else Payment.objects.all()
    orders = WorkOrder.objects.filter(garage=garage) if garage else WorkOrder.objects.all()
    
    total_revenue = sum(float(p.amount) for p in payments)
    completed = orders.filter(status='Completed').count()
    active = orders.filter(status__in=['In Progress', 'Awaiting Parts']).count()
    avg_value = round(total_revenue / completed) if completed > 0 else 0
    
    return JsonResponse({
        'total_revenue': total_revenue,
        'completed_jobs': completed,
        'active_jobs': active,
        'avg_job_value': avg_value,
        'total_customers': Customer.objects.filter(garage=garage).count() if garage else Customer.objects.count(),
    })
