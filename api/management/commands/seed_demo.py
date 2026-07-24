from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import *

class Command(BaseCommand):
    help = 'Seed demo data for pilot garage'

    def handle(self, *args, **kwargs):
        # Create demo owner user first
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={'is_active': True}
        )
        user.set_password('demo1234')
        user.save()

        # Create demo garage with owner
        garage, _ = Garage.objects.get_or_create(
            name='Demo Garage Ltd',
            defaults={
                'owner': user,
                'phone': '+265888000111',
                'address': 'Lilongwe, Malawi'
            }
        )

        UserRole.objects.get_or_create(
            user=user,
            defaults={'role': 'owner', 'garage': garage}
        )

        # Create mechanic user
        mech_user, _ = User.objects.get_or_create(
            username='mechanic1',
            defaults={'is_active': True}
        )
        mech_user.set_password('demo1234')
        mech_user.save()

        mech, _ = MechanicProfile.objects.get_or_create(
            user=mech_user,
            defaults={
                'garage': garage,
                'skills': 'Engine, Brakes, Electrical, Suspension',
                'is_available': True,
                'phone': '+265999111444'
            }
        )

        UserRole.objects.get_or_create(
            user=mech_user,
            defaults={'role': 'mechanic', 'garage': garage}
        )

        # Create customers
        customers = []
        for name, phone in [
            ('John Banda', '+265999111222'),
            ('Mary Phiri', '+265999222333'),
            ('Peter Mwale', '+265999333444'),
            ('Grace Tembo', '+265999444555'),
            ('David Chirwa', '+265999555666'),
        ]:
            c, _ = Customer.objects.get_or_create(
                full_name=name,
                defaults={
                    'garage': garage,
                    'phone': phone,
                    'email': f'{name.lower().replace(" ","")}@email.com'
                }
            )
            customers.append(c)

        # Create vehicles
        vehicles = []
        vehicle_data = [
            (customers[0], 'Toyota', 'Hilux', '2018', 'BT1234', 76500),
            (customers[1], 'Mazda', 'Demio', '2020', 'MH6789', 45000),
            (customers[2], 'Nissan', 'X-Trail', '2019', 'NT3456', 89000),
            (customers[3], 'Honda', 'Fit', '2021', 'HF7890', 32000),
            (customers[4], 'Ford', 'Ranger', '2017', 'FR4567', 120000),
        ]
        for cust, make, model, year, plate, mileage in vehicle_data:
            v, _ = Vehicle.objects.get_or_create(
                plate=plate,
                defaults={
                    'customer': cust, 'garage': garage,
                    'make': make, 'model_name': model,
                    'year': year, 'vin': f'VIN{plate}', 'mileage': mileage
                }
            )
            vehicles.append(v)

        # Create work orders
        wo_data = [
            (vehicles[0], 'In Progress', 45000, 'Engine misfiring, check engine light on'),
            (vehicles[1], 'Awaiting Parts', 28000, 'Brake pads worn, grinding noise'),
            (vehicles[2], 'Ready (Pending Invoice)', 65000, 'Suspension knock on front left'),
            (vehicles[3], 'Completed', 35000, 'Oil change and filter replacement'),
            (vehicles[4], 'Completed', 22000, 'Air conditioning not cooling'),
        ]
        for i, (vehicle, status, cost, issue) in enumerate(wo_data):
            wo, _ = WorkOrder.objects.get_or_create(
                srn=f'BG-{10001 + i}',
                defaults={
                    'vehicle': vehicle, 'garage': garage,
                    'mechanic': mech_user if i < 3 else None,
                    'status': status, 'issue_description': issue,
                    'cost_estimate': cost
                }
            )
            if status == 'Completed':
                Payment.objects.get_or_create(
                    work_order=wo,
                    defaults={
                        'amount': cost,
                        'payment_method': 'Cash',
                        'transaction_ref': f'TXN-{10001 + i}'
                    }
                )

        # Create inventory
        for name, qty, min_th, price in [
            ('Oil Filter', 25, 10, 3500),
            ('Brake Pads (Front)', 8, 5, 12500),
            ('Engine Oil 5L', 15, 8, 18000),
            ('Air Filter', 12, 5, 4500),
            ('Spark Plugs (Set)', 6, 4, 9500),
            ('Shock Absorber', 3, 2, 28000),
            ('Battery 12V', 4, 3, 45000),
            ('Fuel Filter', 10, 5, 3200),
        ]:
            InventoryItem.objects.get_or_create(
                part_name=name, garage=garage,
                defaults={'quantity': qty, 'min_threshold': min_th, 'unit_price': price}
            )

        # Create appointments
        from datetime import date, timedelta
        today = date.today()
        for i, (cust, reason) in enumerate([
            (customers[0], 'Full service checkup'),
            (customers[2], 'Engine diagnostic'),
            (customers[4], 'Brake inspection'),
        ]):
            Appointment.objects.get_or_create(
                customer=cust, garage=garage,
                date=str(today + timedelta(days=i+1)),
                time=f'{8+i*2:02d}:00',
                defaults={'reason': reason}
            )

        # Create service catalog
        for name, cat, desc, price, hours in [
            ('Oil Change', 'Engine', 'Full oil drain and refill with new filter', 18000, 0.5),
            ('Brake Service', 'Brakes', 'Pad replacement and rotor inspection', 25000, 1.0),
            ('Engine Diagnostic', 'Engine', 'Full OBD-II scan and fault analysis', 15000, 1.0),
            ('Suspension Repair', 'Suspension', 'Shock absorber replacement and alignment', 45000, 2.0),
            ('Wheel Alignment', 'Suspension', '4-wheel laser alignment', 12000, 0.5),
            ('AC Service', 'Electrical', 'Refrigerant recharge and system check', 22000, 1.5),
        ]:
            ServiceCatalog.objects.get_or_create(
                name=name, garage=garage,
                defaults={
                    'category': cat, 'description': desc,
                    'base_price': price, 'estimated_hours': hours
                }
            )

        # Welcome notification
        Notification.objects.get_or_create(
            garage=garage, title='Welcome to AutoGarage Pro',
            defaults={
                'message': 'Your demo garage is ready. Explore the dashboard, create work orders, and test AI diagnostics.',
                'type': 'system', 'priority': 'medium'
            }
        )

        self.stdout.write(self.style.SUCCESS('Done! Login: demo / demo1234'))
