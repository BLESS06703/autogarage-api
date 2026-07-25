const API = '/api';
const token = localStorage.getItem('token');
if (!token) { window.location.href = '/api/auth/login-page/'; }

async function api(p, m='GET', b=null) {
    const o = { method:m, headers:{'Authorization':`Bearer ${token}`,'Content-Type':'application/json'} };
    if (b) o.body = JSON.stringify(b);
    const r = await fetch(`${API}${p}`, o);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
}
function L(d) { return Array.isArray(d) ? d : (d&&d.results ? d.results : []); }

// ===== NAVIGATION =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const btn = document.getElementById('hamburgerBtn');
    sidebar.classList.toggle('open');
    btn.innerHTML = sidebar.classList.contains('open') ? '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
}

document.querySelectorAll('.nav-item[data-section]').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        this.classList.add('active');
        closeSidebar();
        document.getElementById('fabMenu').classList.remove('open');
        loadSection(this.dataset.section);
    });
});

function toggleFab() { document.getElementById('fabMenu').classList.toggle('open'); }

// ===== SECTION LOADER =====
async function loadSection(s) {
    closeSidebar();
    const m = document.getElementById('main-content');
    m.innerHTML = '<div style="text-align:center;padding:60px;"><div class="loading-spinner"></div></div>';
    // Show/hide hamburger
    const hb = document.getElementById('hamburgerBtn');
    if (s === 'dashboard') { if (window.innerWidth <= 768) hb.style.display = 'flex'; }
    else { hb.style.display = 'none'; }
    try {
        const fns = {dashboard:dash, workorders:wo, customers:cust, vehicles:veh, mechanics:mech, inventory:inv, appointments:appt, payments:pay, invoices:invc, reports:rpt, ai:aid, notifications:notif, settings:sett};
        if (fns[s]) await fns[s](); else throw new Error('Section not found');
    } catch(e) {
        m.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>${e.message}</p><button class="btn btn-outline" style="margin-top:14px;" onclick="loadSection('${s}')">Retry</button></div>`;
    }
}

// ===== DASHBOARD =====
async function dash() {
    const now = new Date();
    const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    const hour = now.getHours();
    const greeting = hour < 12 ? 'Good Morning' : hour < 17 ? 'Good Afternoon' : 'Good Evening';
    const dateStr = `${days[now.getDay()]}, ${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;

    document.getElementById('main-content').innerHTML = `
        <div class="welcome">
            <div class="welcome-greeting">${greeting} &#128075;</div>
            <div class="welcome-name">AutoGarage Pro</div>
            <div class="welcome-date">${dateStr} &middot; Today's Overview</div>
        </div>
        <div class="kpi-grid">
            <div class="kpi-card" onclick="loadSection('customers')"><div class="kpi-icon icon-blue"><i class="fas fa-users"></i></div><div class="kpi-label">Customers</div><div class="kpi-value" id="k1" style="color:var(--blue);">-</div><div class="kpi-sub">Registered</div></div>
            <div class="kpi-card" onclick="loadSection('vehicles')"><div class="kpi-icon icon-purple"><i class="fas fa-car"></i></div><div class="kpi-label">Vehicles</div><div class="kpi-value" id="k2" style="color:var(--purple);">-</div><div class="kpi-sub">In service</div></div>
            <div class="kpi-card" onclick="loadSection('workorders')"><div class="kpi-icon icon-orange"><i class="fas fa-clipboard-list"></i></div><div class="kpi-label">Active Jobs</div><div class="kpi-value" id="k3" style="color:var(--orange);">-</div><div class="kpi-sub">Urgent</div></div>
            <div class="kpi-card" onclick="loadSection('reports')"><div class="kpi-icon icon-green"><i class="fas fa-chart-bar"></i></div><div class="kpi-label">Revenue</div><div class="kpi-value" id="k4" style="color:var(--green);">-</div><div class="kpi-sub">Today</div></div>
        </div>
        <div class="content-grid">
            <div class="card"><div class="card-title"><i class="fas fa-clock"></i> Recent Activity</div><div id="activity"></div></div>
            <div class="card"><div class="card-title"><i class="fas fa-bolt"></i> Quick Actions</div>
                <button class="btn btn-primary" style="width:100%;margin-bottom:8px;" onclick="showQuickIntake()"><i class="fas fa-plus"></i> New Work Order</button>
                <button class="btn btn-outline" style="width:100%;margin-bottom:8px;" onclick="showCustomerModal()"><i class="fas fa-user-plus"></i> Register Customer</button>
                <button class="btn btn-outline" style="width:100%;margin-bottom:8px;" onclick="showVehicleModal()"><i class="fas fa-car"></i> Register Vehicle</button>
                <button class="btn btn-outline" style="width:100%;" onclick="showInventoryModal()"><i class="fas fa-box"></i> Add Inventory</button>
            </div>
        </div>`;
    // Load KPIs with a single lightweight call
    try {
        const data = await api('/charts/all/');
        document.getElementById('k1').textContent = data.total_customers || 0;
        document.getElementById('k2').textContent = data.active_jobs || 0;
        document.getElementById('k3').textContent = (data.active_jobs || 0) + (data.completed_jobs || 0);
        document.getElementById('k4').textContent = 'MWK ' + (data.total_revenue || 0).toLocaleString();
        document.getElementById('activity').innerHTML = '<div class="empty-state"><p>Click Work Orders to view</p></div>';
    } catch(e) {}
}

// ===== WORK ORDERS =====
async function wo() {
    const list = L(await api('/work-orders/'));
    const sc = {'In Progress':'tag-progress','Awaiting Parts':'tag-parts','Ready (Pending Invoice)':'tag-invoice','Completed':'tag-done'};
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Work Orders</h1><button class="btn btn-primary" onclick="showQuickIntake()"><i class="fas fa-plus"></i> New</button></div>
        <div class="card">
            <div class="search-wrap"><i class="fas fa-search"></i><input class="search-input" id="woS" placeholder="Search..." oninput="FT('woS','woB')"></div>
            <div class="filter-chips">
                <button class="filter-chip active" onclick="filterWO('all',this)">All</button>
                <button class="filter-chip" onclick="filterWO('In Progress',this)">In Progress</button>
                <button class="filter-chip" onclick="filterWO('Awaiting Parts',this)">Awaiting Parts</button>
                <button class="filter-chip" onclick="filterWO('Ready (Pending Invoice)',this)">Pending Invoice</button>
                <button class="filter-chip" onclick="filterWO('Completed',this)">Completed</button>
            </div>
            <div class="table-wrapper"><table><thead><tr><th>SRN</th><th>Vehicle</th><th>Status</th><th>Cost</th><th>Actions</th></tr></thead>
            <tbody id="woB">${list.map(w=>`<tr><td class="text-mono">${w.srn||'BG-'+w.id}</td><td>${w.vehicle_info||w.vehicle||'--'}</td><td><span class="tag ${sc[w.status]||'tag-progress'}">${w.status}</span></td><td class="text-mono">MWK ${parseFloat(w.cost_estimate||0).toLocaleString()}</td><td>
                <button class="btn btn-outline btn-sm" onclick="event.stopPropagation();editWO(${w.id},'${(w.vehicle_info||'').replace(/'/g,"\\'")}','${(w.customer_name||'').replace(/'/g,"\\'")}',${parseFloat(w.cost_estimate||0)})"><i class="fas fa-edit"></i></button>
                <button class="btn btn-outline btn-sm" style="color:var(--red);border-color:var(--red);" onclick="event.stopPropagation();confirmDelete('Delete WO?','Remove #${w.srn||w.id}?',()=>deleteWO(${w.id}))"><i class="fas fa-trash"></i></button>
                <select onchange="woUp(${w.id},this.value)" style="padding:5px 8px;background:var(--surface2);color:var(--text);border:1px solid var(--border);border-radius:5px;font-size:11px;margin-left:4px;"><option>Status</option><option>In Progress</option><option>Awaiting Parts</option><option>Ready (Pending Invoice)</option><option>Completed</option></select>
            </td></tr>`).join('')||'<tr><td colspan="5"><div class="empty-state"><i class="fas fa-clipboard-list"></i><p>No work orders</p><button class="btn btn-primary" style="margin-top:12px;" onclick="showQuickIntake()">Create First Work Order</button></div></td></tr>'}</tbody></table></div>
        </div>`;
}

// ===== CUSTOMERS =====
async function cust() {
    const list = L(await api('/customers/'));
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Customers</h1></div>
        <div class="card">
            <div class="search-wrap"><i class="fas fa-search"></i><input class="search-input" id="cs" placeholder="Search..." oninput="FT('cs','cb')"></div>
            <div class="table-wrapper"><table><thead><tr><th>Customer</th><th>Phone</th><th>Email</th><th>Registered</th><th></th></tr></thead>
            <tbody id="cb">${list.map(c=>`<tr onclick="custProfile(${c.id},'${c.full_name.replace(/'/g,"\\'")}','${c.phone||''}','${c.email||''}','${c.reference_number||''}')"><td><div style="display:flex;align-items:center;gap:10px;"><div style="width:34px;height:34px;border-radius:50%;background:var(--orange);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:13px;">${(c.full_name||'?')[0]}</div><div><strong>${c.full_name}</strong><div class="text-mono" style="color:var(--text2);">${c.reference_number||'--'}</div></div></div></td><td><i class="fas fa-phone" style="color:var(--text2);margin-right:6px;"></i>${c.phone||'--'}</td><td><i class="fas fa-envelope" style="color:var(--text2);margin-right:6px;"></i>${c.email||'--'}</td><td>${(c.created_at||'').substring(0,10)}</td><td><i class="fas fa-chevron-right" style="color:var(--text2);"></i></td></tr>`).join('')||'<tr><td colspan="5"><div class="empty-state"><i class="fas fa-users"></i><p>No customers</p><button class="btn btn-primary" style="margin-top:12px;" onclick="showCustomerModal()">Register First Customer</button></div></td></tr>'}</tbody></table></div>
        </div>`;
}
function custProfile(id,name,phone,email,ref){
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('customers')"><i class="fas fa-arrow-left"></i> Back</button><h1>Customer Profile</h1></div>
        <div class="profile-header"><div class="profile-avatar">${name[0]}</div><div><h2 style="font-size:20px;">${name}</h2><p style="color:var(--text2);font-size:12px;">${ref}</p><p style="color:var(--text2);font-size:12px;"><i class="fas fa-phone"></i> ${phone||'N/A'} &middot; <i class="fas fa-envelope"></i> ${email||'N/A'}</p></div></div>
        <div class="card"><div class="card-title">Vehicles & History</div><p style="color:var(--text2);">Loading...</p></div>`;
}

// ===== VEHICLES =====
async function veh() {
    const list = L(await api('/vehicles/'));
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Vehicles</h1></div>
        <div class="card">
            <div class="search-wrap"><i class="fas fa-search"></i><input class="search-input" id="vs" placeholder="Search..." oninput="FT('vs','vb')"></div>
            <div class="table-wrapper"><table><thead><tr><th>Vehicle</th><th>Plate</th><th>Year</th><th>Mileage</th><th>Actions</th></tr></thead>
            <tbody id="vb">${list.map(v=>`<tr onclick="vehProfile(${v.id},'${v.make||''}','${v.model_name||''}','${v.plate||''}','${v.year||''}',${v.mileage||0})"><td><div style="display:flex;align-items:center;gap:10px;"><div style="width:36px;height:36px;border-radius:10px;background:rgba(139,92,246,0.15);display:flex;align-items:center;justify-content:center;color:var(--purple);"><i class="fas fa-car"></i></div><div><strong>${v.make} ${v.model_name}</strong></div></div></td><td class="text-mono" style="color:var(--orange);font-weight:600;">${v.plate||'--'}</td><td>${v.year||'--'}</td><td>${(v.mileage||0).toLocaleString()} km</td><td>
                <button class="btn btn-outline btn-sm" onclick="event.stopPropagation();editVeh(${v.id},'${v.make||''}','${v.model_name||''}','${v.plate||''}','${v.year||''}',${v.mileage||0})"><i class="fas fa-edit"></i></button>
                <button class="btn btn-outline btn-sm" style="color:var(--red);border-color:var(--red);" onclick="event.stopPropagation();confirmDelete('Delete Vehicle?','Remove ${v.plate||v.make}?',()=>deleteVeh(${v.id}))"><i class="fas fa-trash"></i></button>
            </td></tr>`).join('')||'<tr><td colspan="5"><div class="empty-state"><i class="fas fa-car"></i><p>No vehicles</p><button class="btn btn-primary" style="margin-top:12px;" onclick="showVehicleModal()">Register First Vehicle</button></div></td></tr>'}</tbody></table></div>
        </div>`;
}
function vehProfile(id,make,model,plate,year,mileage){
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('vehicles')"><i class="fas fa-arrow-left"></i> Back</button><h1>Vehicle Profile</h1></div>
        <div class="profile-header"><div class="profile-avatar" style="background:var(--purple);"><i class="fas fa-car"></i></div><div><h2 style="font-size:20px;">${make} ${model}</h2><p class="text-mono" style="color:var(--orange);font-weight:600;font-size:14px;">${plate}</p><p style="color:var(--text2);font-size:12px;">${year} &middot; ${mileage.toLocaleString()} km</p></div></div>
        <div class="card"><div class="card-title"><i class="fas fa-history"></i> Service Timeline</div><div class="timeline"><div class="timeline-item">Vehicle registered</div></div></div>`;
}

// ===== MECHANICS =====
async function mech() {
    const list = L(await api('/mechanics/'));
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Mechanics</h1></div>
        <div class="card"><div class="table-wrapper"><table><thead><tr><th>Mechanic</th><th>Skills</th><th>Phone</th><th>Status</th></tr></thead>
        <tbody>${list.map(m=>`<tr><td><div style="display:flex;align-items:center;gap:10px;"><div style="width:34px;height:34px;border-radius:50%;background:var(--blue);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:13px;">${(m.full_name||m.username||'?')[0]}</div><strong>${m.full_name||m.username||'--'}</strong></div></td><td>${m.skills||'--'}</td><td>${m.phone||'--'}</td><td><span class="tag ${m.is_available?'tag-done':'tag-progress'}">${m.is_available?'Available':'Busy'}</span></td></tr>`).join('')||'<tr><td colspan="4"><div class="empty-state"><i class="fas fa-user-cog"></i><p>No mechanics</p></div></td></tr>'}</tbody></table></div></div>`;
}

// ===== INVENTORY =====
async function inv() {
    const list = L(await api('/inventory/'));
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Inventory</h1></div>
        <div class="card">
            <div class="search-wrap"><i class="fas fa-search"></i><input class="search-input" id="is" placeholder="Search..." oninput="FT('is','ib')"></div>
            <div class="filter-chips">
                <button class="filter-chip active" onclick="filterInv('all',this)">All</button>
                <button class="filter-chip" onclick="filterInv('low',this)">Low Stock</button>
                <button class="filter-chip" onclick="filterInv('ok',this)">In Stock</button>
            </div>
            <div class="table-wrapper"><table><thead><tr><th>Part</th><th>Qty</th><th>Min</th><th>Price</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody id="ib">${list.map(i=>{const lo=i.quantity<i.min_threshold;return`<tr><td><strong>${i.part_name}</strong></td><td class="text-mono" style="color:${lo?'var(--red)':'var(--green)'};font-weight:600;">${i.quantity}</td><td>${i.min_threshold}</td><td class="text-mono">MWK ${parseFloat(i.unit_price||0).toLocaleString()}</td><td><span class="tag ${lo?'tag-parts':'tag-done'}">${lo?'Low Stock':'In Stock'}</span></td><td>
                <button class="btn btn-outline btn-sm" onclick="editInv(${i.id},'${(i.part_name||'').replace(/'/g,"\\'")}',${i.quantity},${i.min_threshold},${parseFloat(i.unit_price||0)})"><i class="fas fa-edit"></i></button>
                <button class="btn btn-outline btn-sm" style="color:var(--red);border-color:var(--red);" onclick="confirmDelete('Delete?','Remove ${(i.part_name||'').replace(/'/g,"\\'")}?',()=>deleteInv(${i.id}))"><i class="fas fa-trash"></i></button>
            </td></tr>`;}).join('')||'<tr><td colspan="6"><div class="empty-state"><i class="fas fa-boxes"></i><p>No items</p><button class="btn btn-primary" style="margin-top:12px;" onclick="showInventoryModal()">Add First Item</button></div></td></tr>'}</tbody></table></div>
        </div>`;
}

// ===== APPOINTMENTS =====
async function appt() {
    const list = L(await api('/appointments/'));
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Appointments</h1></div>
        <div class="card"><div class="table-wrapper"><table><thead><tr><th>Date</th><th>Time</th><th>Customer</th><th>Reason</th></tr></thead>
        <tbody>${list.map(a=>`<tr><td>${a.date||'--'}</td><td class="text-mono" style="color:var(--orange);font-weight:600;">${a.time||'--:--'}</td><td><strong>${a.customer_name||a.customer||'--'}</strong></td><td>${a.reason||'--'}</td></tr>`).join('')||'<tr><td colspan="4"><div class="empty-state"><i class="fas fa-calendar-alt"></i><p>No appointments</p></div></td></tr>'}</tbody></table></div></div>`;
}

// ===== PAYMENTS =====
async function pay() {
    const list = L(await api('/payments/'));
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Payments</h1></div>
        <div class="card"><div class="table-wrapper"><table><thead><tr><th>Ref</th><th>Amount</th><th>Method</th><th>Date</th></tr></thead>
        <tbody>${list.map(p=>`<tr><td class="text-mono">${p.transaction_ref||'--'}</td><td class="text-mono" style="color:var(--green);font-weight:600;">MWK ${parseFloat(p.amount||0).toLocaleString()}</td><td>${p.payment_method||'--'}</td><td>${(p.created_at||'').substring(0,10)}</td></tr>`).join('')||'<tr><td colspan="4"><div class="empty-state"><i class="fas fa-money-bill-wave"></i><p>No payments</p></div></td></tr>'}</tbody></table></div></div>`;
}

// ===== INVOICES =====
async function invc() {
    const list = L(await api('/invoices/'));
    const sc={paid:'tag-done',sent:'tag-invoice',draft:'tag-parts',cancelled:'tag-cancelled'};
    document.getElementById('main-content').innerHTML = `
        <div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Invoices</h1></div>
        <div class="card"><div class="table-wrapper"><table><thead><tr><th>Invoice #</th><th>Customer</th><th>Total</th><th>Status</th></tr></thead>
        <tbody>${list.map(i=>`<tr><td class="text-mono">${i.invoice_number||'INV-'+i.id}</td><td><strong>${i.customer_name||'--'}</strong></td><td class="text-mono" style="color:var(--green);font-weight:600;">MWK ${parseFloat(i.total_amount||0).toLocaleString()}</td><td><span class="tag ${sc[i.status]||'tag-progress'}">${(i.status||'draft').toUpperCase()}</span></td></tr>`).join('')||'<tr><td colspan="4"><div class="empty-state"><i class="fas fa-file-invoice"></i><p>No invoices</p></div></td></tr>'}</tbody></table></div></div>`;
}

// ===== REPORTS =====
async function rpt() {
    document.getElementById('main-content').innerHTML = `<div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Reports</h1></div><div style="text-align:center;padding:40px;"><div class="loading-spinner"></div></div>`;
    try{
        const [o,p,m]=await Promise.all([api('/work-orders/'),api('/payments/'),api('/mechanics/')]);
        const wo=L(o),pa=L(p),me=L(m);
        const rev=pa.reduce((s,p)=>s+(parseFloat(p.amount)||0),0),comp=wo.filter(w=>w.status==='Completed').length,act=wo.filter(w=>w.status==='In Progress'||w.status==='Awaiting Parts').length,avg=comp>0?Math.round(rev/comp):0;
        const st={'In Progress':0,'Awaiting Parts':0,'Ready (Pending Invoice)':0,'Completed':0};wo.forEach(w=>{if(st[w.status]!==undefined)st[w.status]++;});
        const mt={};pa.forEach(p=>{const m=p.payment_method||'Other';mt[m]=(mt[m]||0)+parseFloat(p.amount||0);});
        const it={};wo.forEach(w=>{const k=(w.issue_description||'General').split(' ').slice(0,3).join(' ');it[k]=(it[k]||0)+1;});
        const top=Object.entries(it).sort((a,b)=>b[1]-a[1]).slice(0,6);
        document.getElementById('main-content').innerHTML = `<div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Reports & Analytics</h1></div>
            <div class="kpi-grid"><div class="kpi-card"><div class="kpi-label">Total Revenue</div><div class="kpi-value" style="color:var(--green);">MWK ${rev.toLocaleString()}</div></div><div class="kpi-card"><div class="kpi-label">Completed</div><div class="kpi-value" style="color:var(--blue);">${comp}</div></div><div class="kpi-card"><div class="kpi-label">Avg Value</div><div class="kpi-value" style="color:var(--orange);">MWK ${avg.toLocaleString()}</div></div><div class="kpi-card"><div class="kpi-label">Active</div><div class="kpi-value" style="color:var(--purple);">${act}</div></div></div>
            <div class="content-grid"><div class="card"><div class="card-title"><i class="fas fa-chart-bar"></i> Revenue by Method</div><div style="height:280px;"><canvas id="c1"></canvas></div></div><div class="card"><div class="card-title"><i class="fas fa-chart-pie"></i> Job Status</div><div style="height:280px;"><canvas id="c2"></canvas></div></div><div class="card"><div class="card-title"><i class="fas fa-chart-line"></i> Common Repairs</div><div style="height:280px;"><canvas id="c3"></canvas></div></div><div class="card"><div class="card-title"><i class="fas fa-user-check"></i> Mechanic Workload</div><div style="height:280px;"><canvas id="c4"></canvas></div></div></div>`;
        setTimeout(()=>{
            const o={responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#888'}}},scales:{x:{ticks:{color:'#888'},grid:{color:'#222'}},y:{ticks:{color:'#888'},grid:{color:'#222'}}}};
            new Chart(document.getElementById('c1'),{type:'bar',data:{labels:Object.keys(mt),datasets:[{label:'Revenue (MWK)',data:Object.values(mt),backgroundColor:['#FF6F00','#3B82F6','#22C55E','#8B5CF6','#F59E0B'],borderRadius:6}]},options:o});
            new Chart(document.getElementById('c2'),{type:'doughnut',data:{labels:Object.keys(st),datasets:[{data:Object.values(st),backgroundColor:['#FF6F00','#F59E0B','#3B82F6','#22C55E'],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:'#888',padding:15}}}}});
            new Chart(document.getElementById('c3'),{type:'line',data:{labels:top.map(i=>i[0]),datasets:[{label:'Occurrences',data:top.map(i=>i[1]),borderColor:'#FF6F00',backgroundColor:'rgba(255,111,0,0.1)',fill:true,tension:0.4,pointBackgroundColor:'#FF6F00'}]},options:o});
            const md=me.slice(0,8).map(m=>({name:m.full_name||m.username||'N/A',jobs:wo.filter(w=>w.mechanic==m.user).length||1}));
            new Chart(document.getElementById('c4'),{type:'polarArea',data:{labels:md.map(m=>m.name),datasets:[{data:md.map(m=>m.jobs),backgroundColor:['#FF6F00','#3B82F6','#22C55E','#8B5CF6','#F59E0B','#EF4444','#EC4899','#14B8A6'],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:'#888',padding:10}}}}});
        },500);
    }catch(e){document.getElementById('main-content').innerHTML=`<div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Reports</h1></div><div class="empty-state"><i class="fas fa-chart-bar"></i><p>No data yet. Create work orders and payments.</p></div>`;}
}

// ===== AI =====
async function aid(){
    document.getElementById('main-content').innerHTML = `<div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>AI Diagnostics</h1></div>
        <div class="card" style="max-width:560px;"><div class="card-title"><i class="fas fa-robot"></i> Fault Code Analyzer</div>
        <div class="form-group"><label>OBD-II Code</label><input id="ac" placeholder="e.g. P0300" maxlength="5" style="text-transform:uppercase;"></div>
        <div class="form-group"><label>Vehicle (optional)</label><input id="av" placeholder="e.g. Toyota Hilux"></div>
        <button class="btn btn-primary" onclick="runAI()"><i class="fas fa-search"></i> Run Diagnosis</button><div id="ar" style="margin-top:14px;"></div></div>`;
}
async function runAI(){
    const c=document.getElementById('ac').value,v=document.getElementById('av').value,el=document.getElementById('ar');
    if(!c){el.innerHTML='<p style="color:var(--red);">Enter a code</p>';return;}
    el.innerHTML='<div class="loading-spinner"></div>';
    try{
        const d=await api('/ai/diagnose/','POST',{code:c,vehicle:v});
        const sc={Critical:'var(--red)',High:'var(--orange)',Medium:'var(--amber)',Low:'var(--green)'};
        el.innerHTML=`<div style="padding:18px;background:var(--surface2);border-radius:10px;border-left:4px solid ${sc[d.severity]||'var(--blue)'};margin-top:12px;"><h3>${d.title}</h3><p style="font-size:12px;color:var(--text2);margin:8px 0;">Severity: <strong>${d.severity}</strong> &middot; Cost: <strong>${d.estimated_cost}</strong></p><ol style="padding-left:18px;font-size:13px;line-height:2;">${d.details.map(x=>`<li>${x}</li>`).join('')}</ol></div>`;
    }catch(e){el.innerHTML=`<p style="color:var(--red);">${e.message}</p>`;}
}

// ===== NOTIFICATIONS =====
async function notif(){
    const list=L(await api('/notifications/'));
    document.getElementById('main-content').innerHTML=`<div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Notifications</h1><button class="btn btn-outline" onclick="markAll()">Mark All Read</button></div>
        <div class="card">${list.map(n=>`<div class="activity-item" style="opacity:${n.is_read?0.5:1};"><span class="activity-dot" style="background:${n.priority==='urgent'?'var(--red)':n.priority==='high'?'var(--orange)':'var(--blue)'};"></span><span style="flex:1;"><strong>${n.title}</strong><span style="font-size:11px;color:var(--text2);display:block;">${n.message}</span></span>${!n.is_read?`<button class="btn btn-outline" style="font-size:10px;padding:4px 10px;" onclick="mr(${n.id})">Read</button>`:''}</div>`).join('')||'<div class="empty-state"><i class="fas fa-bell"></i><p>No notifications</p></div>'}</div>`;
    window._nl=list;
}
async function mr(id){await api(`/notifications/${id}/`,'PATCH',{is_read:true});loadSection('notifications');}
async function markAll(){for(const n of(window._nl||[])){if(!n.is_read)await api(`/notifications/${n.id}/`,'PATCH',{is_read:true});}loadSection('notifications');}

// ===== SETTINGS =====
async function sett(){
    document.getElementById('main-content').innerHTML=`<div class="page-header"><button class="back-btn" onclick="loadSection('dashboard')"><i class="fas fa-arrow-left"></i> Back</button><h1>Settings</h1></div>
        <div class="card" style="max-width:480px;"><table style="width:100%;"><tr><td style="padding:10px 0;color:var(--text2);">Platform</td><td>AutoGarage Pro v2.0</td></tr><tr><td style="padding:10px 0;color:var(--text2);">Status</td><td style="color:var(--green);">Connected</td></tr></table>
        <button class="btn btn-outline" style="width:100%;margin-top:14px;" onclick="testConn()">Test Connection</button>
        <button class="btn btn-danger" style="width:100%;margin-top:8px;" onclick="logout()">Sign Out</button><div id="tr" style="margin-top:10px;font-size:12px;"></div></div>`;
}
async function testConn(){const e=document.getElementById('tr');e.innerHTML='<div class="loading-spinner"></div>';const s=Date.now();try{await api('/dashboard/');e.innerHTML=`<span style="color:var(--green);">Connected (${Date.now()-s}ms)</span>`;}catch(x){e.innerHTML=`<span style="color:var(--red);">${x.message}</span>`;}}

// ===== CRUD OPERATIONS =====
async function woUp(id,s){if(!s)return;await api(`/work-orders/${id}/`,'PATCH',{status:s});loadSection('workorders');showToast('Status updated','success');}
async function deleteWO(id){await api(`/work-orders/${id}/`,'DELETE');loadSection('workorders');showToast('Deleted','success');}
async function deleteInv(id){await api(`/inventory/${id}/`,'DELETE');loadSection('inventory');showToast('Deleted','success');}
async function deleteVeh(id){await api(`/vehicles/${id}/`,'DELETE');loadSection('vehicles');showToast('Deleted','success');}

function editWO(id, vehicle, customer, cost) {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal"><div class="modal-title">Edit Work Order</div>
        <div class="form-group"><label>Vehicle</label><input id="ewv" value="${vehicle}"></div>
        <div class="form-group"><label>Customer</label><input id="ewc" value="${customer}"></div>
        <div class="form-group"><label>Cost (MWK)</label><input id="ewk" type="number" value="${cost}"></div>
        <div class="form-actions"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" onclick="updateWO(${id})">Save</button></div></div>`;
    document.body.appendChild(ov);
}
async function updateWO(id) {
    await api(`/work-orders/${id}/`, 'PATCH', { vehicle_info: document.getElementById('ewv').value, customer_name: document.getElementById('ewc').value, cost_estimate: parseFloat(document.getElementById('ewk').value) });
    document.querySelector('.modal-overlay').remove(); showToast('Updated', 'success'); loadSection('workorders');
}

function editInv(id, name, qty, min, price) {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal"><div class="modal-title">Edit ${name}</div>
        <div class="form-group"><label>Name</label><input id="einv" value="${name}"></div>
        <div class="form-group"><label>Qty</label><input id="einvq" type="number" value="${qty}"></div>
        <div class="form-group"><label>Min</label><input id="einvmin" type="number" value="${min}"></div>
        <div class="form-group"><label>Price</label><input id="einvp" type="number" value="${price}"></div>
        <div class="form-actions"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" onclick="updateInv(${id})">Save</button></div></div>`;
    document.body.appendChild(ov);
}
async function updateInv(id) {
    await api(`/inventory/${id}/`, 'PATCH', { part_name: document.getElementById('einv').value, quantity: parseInt(document.getElementById('einvq').value), min_threshold: parseInt(document.getElementById('einvmin').value), unit_price: parseFloat(document.getElementById('einvp').value) });
    document.querySelector('.modal-overlay').remove(); showToast('Updated', 'success'); loadSection('inventory');
}

function editVeh(id, make, model, plate, year, mileage) {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal"><div class="modal-title">Edit Vehicle</div>
        <div class="form-group"><label>Make</label><input id="evmake" value="${make}"></div>
        <div class="form-group"><label>Model</label><input id="evmodel" value="${model}"></div>
        <div class="form-group"><label>Plate</label><input id="evplate" value="${plate}"></div>
        <div class="form-group"><label>Year</label><input id="evyear" value="${year}"></div>
        <div class="form-group"><label>Mileage</label><input id="evmile" type="number" value="${mileage}"></div>
        <div class="form-actions"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" onclick="updateVeh(${id})">Save</button></div></div>`;
    document.body.appendChild(ov);
}
async function updateVeh(id) {
    await api(`/vehicles/${id}/`, 'PATCH', { make: document.getElementById('evmake').value, model_name: document.getElementById('evmodel').value, plate: document.getElementById('evplate').value, year: document.getElementById('evyear').value, mileage: parseInt(document.getElementById('evmile').value) });
    document.querySelector('.modal-overlay').remove(); showToast('Updated', 'success'); loadSection('vehicles');
}

// ===== CREATE MODALS =====
function showQuickIntake() {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal" style="max-width:600px;"><div class="modal-title"><i class="fas fa-clipboard-list"></i> New Job Intake</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div><div class="form-group"><label>Customer Name *</label><input id="qiName" placeholder="Full name"></div></div>
            <div><div class="form-group"><label>Phone</label><input id="qiPhone" placeholder="+265..."></div></div>
            <div><div class="form-group"><label>Vehicle Make *</label><input id="qiMake" placeholder="Toyota"></div></div>
            <div><div class="form-group"><label>Vehicle Model *</label><input id="qiModel" placeholder="Hilux"></div></div>
            <div><div class="form-group"><label>Plate Number *</label><input id="qiPlate" placeholder="BT1234"></div></div>
            <div><div class="form-group"><label>Year</label><input id="qiYear" placeholder="2018"></div></div>
            <div><div class="form-group"><label>Mileage</label><input id="qiMileage" type="number" value="0"></div></div>
            <div><div class="form-group"><label>Cost Estimate (MWK)</label><input id="qiCost" type="number" value="0"></div></div>
        </div>
        <div class="form-group"><label>Issue / Problem Description *</label><textarea id="qiIssue" placeholder="Describe what needs to be fixed..."></textarea></div>
        <div class="form-actions"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" onclick="submitIntake()"><i class="fas fa-save"></i> Submit Job</button></div></div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click', e => { if (e.target === ov) ov.remove(); });
}

async function submitIntake() {
    const name = document.getElementById('qiName').value.trim();
    const make = document.getElementById('qiMake').value.trim();
    const model = document.getElementById('qiModel').value.trim();
    const plate = document.getElementById('qiPlate').value.trim();
    const issue = document.getElementById('qiIssue').value.trim();
    
    if (!name) return showToast('Customer name required', 'error');
    if (!make || !model) return showToast('Vehicle make and model required', 'error');
    if (!plate) return showToast('Plate number required', 'error');
    if (!issue) return showToast('Issue description required', 'error');
    
    try {
        await api('/intake/', 'POST', {
            customer_name: name,
            customer_phone: document.getElementById('qiPhone').value,
            vehicle_make: make,
            vehicle_model: model,
            vehicle_plate: plate,
            vehicle_year: document.getElementById('qiYear').value,
            vehicle_mileage: parseInt(document.getElementById('qiMileage').value) || 0,
            issue_description: issue,
            cost_estimate: parseFloat(document.getElementById('qiCost').value) || 0
        });
        document.querySelector('.modal-overlay').remove();
        showToast('Job intake complete!', 'success');
        loadSection('dashboard');
    } catch(e) {
        showToast('Failed: ' + e.message, 'error');
    }
}

// Keep old modal as fallback, but point to new one
function showWOModal() {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal"><div class="modal-title">New Work Order</div>
        <div class="form-group"><label>Vehicle</label><input id="wv" placeholder="e.g. Toyota Hilux"></div>
        <div class="form-group"><label>Customer Name</label><input id="wc" placeholder="Customer name"></div>
        <div class="form-group"><label>Issue</label><textarea id="wi"></textarea></div>
        <div class="form-group"><label>Cost (MWK)</label><input id="wk" type="number" value="0"></div>
        <div class="form-actions"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" onclick="createWO()">Create</button></div></div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click', e => { if (e.target === ov) ov.remove(); });
}
async function createWO() {
    const v=document.getElementById('wv').value.trim(), c=document.getElementById('wc').value.trim();
    if(!v) { showToast('Vehicle name is required', 'error'); return; }
    if(!c) { showToast('Customer name is required', 'error'); return; }
    await api('/work-orders/','POST',{vehicle_info:v,customer_name:c,issue_description:document.getElementById('wi').value,cost_estimate:parseFloat(document.getElementById('wk').value)||0});
    document.querySelector('.modal-overlay').remove(); showToast('Work order created','success'); loadSection('workorders');
}

function showCustomerModal() {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal"><div class="modal-title">Register Customer</div>
        <div class="form-group"><label>Full Name</label><input id="cmName" placeholder="Customer name"></div>
        <div class="form-group"><label>Phone</label><input id="cmPhone" placeholder="+265..."></div>
        <div class="form-group"><label>Email</label><input id="cmEmail" placeholder="email@example.com"></div>
        <div class="form-actions"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" onclick="createCustomer()">Register</button></div></div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click', e => { if (e.target === ov) ov.remove(); });
}
async function createCustomer() {
    const n=document.getElementById('cmName').value.trim();
    const p=document.getElementById('cmPhone').value.trim();
    if(!n) { showToast('Customer name is required', 'error'); return; }
    await api('/customers/','POST',{full_name:n,phone:document.getElementById('cmPhone').value,email:document.getElementById('cmEmail').value});
    document.querySelector('.modal-overlay').remove(); showToast('Customer registered','success'); loadSection('customers');
}

function showVehicleModal() {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal"><div class="modal-title">Register Vehicle</div>
        <div class="form-group"><label>Make</label><input id="vmMake" placeholder="Toyota"></div>
        <div class="form-group"><label>Model</label><input id="vmModel" placeholder="Hilux"></div>
        <div class="form-group"><label>Plate</label><input id="vmPlate" placeholder="BT1234"></div>
        <div class="form-group"><label>Year</label><input id="vmYear" placeholder="2018"></div>
        <div class="form-group"><label>Mileage</label><input id="vmMileage" type="number" value="0"></div>
        <div class="form-actions"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" onclick="createVehicle()">Register</button></div></div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click', e => { if (e.target === ov) ov.remove(); });
}
async function createVehicle() {
    const mk=document.getElementById('vmMake').value.trim(), md=document.getElementById('vmModel').value.trim(), pl=document.getElementById('vmPlate').value.trim();
    if(!mk) { showToast('Vehicle make is required', 'error'); return; }
    if(!md) { showToast('Vehicle model is required', 'error'); return; }
    if(!pl) { showToast('Plate number is required', 'error'); return; }
    await api('/vehicles/','POST',{make:mk,model_name:md,plate:pl,year:document.getElementById('vmYear').value,mileage:parseInt(document.getElementById('vmMileage').value)||0});
    document.querySelector('.modal-overlay').remove(); showToast('Vehicle registered','success'); loadSection('vehicles');
}

function showInventoryModal() {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal"><div class="modal-title">Add Inventory</div>
        <div class="form-group"><label>Part Name</label><input id="imName" placeholder="Oil Filter"></div>
        <div class="form-group"><label>Quantity</label><input id="imQty" type="number" value="1"></div>
        <div class="form-group"><label>Min Threshold</label><input id="imMin" type="number" value="5"></div>
        <div class="form-group"><label>Unit Price (MWK)</label><input id="imPrice" type="number" value="0"></div>
        <div class="form-actions"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-primary" onclick="createInventory()">Add</button></div></div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click', e => { if (e.target === ov) ov.remove(); });
}
async function createInventory() {
    const n=document.getElementById('imName').value.trim();
    if(!n) { showToast('Part name is required', 'error'); return; }
    await api('/inventory/','POST',{part_name:n,quantity:parseInt(document.getElementById('imQty').value)||1,min_threshold:parseInt(document.getElementById('imMin').value)||5,unit_price:parseFloat(document.getElementById('imPrice').value)||0});
    document.querySelector('.modal-overlay').remove(); showToast('Item added','success'); loadSection('inventory');
}

// ===== HELPERS =====
let woFilter = 'all', invFilter = 'all';
function filterWO(status, btn) { woFilter = status; document.querySelectorAll('#main-content .filter-chip').forEach(c=>c.classList.remove('active')); if(btn) btn.classList.add('active'); FT('woS','woB'); }
function filterInv(status, btn) { invFilter = status; document.querySelectorAll('#main-content .filter-chip').forEach(c=>c.classList.remove('active')); if(btn) btn.classList.add('active'); FT('is','ib'); }
function FT(s,t){
    const q=document.getElementById(s).value.toLowerCase();
    document.querySelectorAll(`#${t} tr`).forEach(r=>{
        const txt=r.textContent.toLowerCase();
        const ms=txt.includes(q);
        const mf=t==='woB'?(woFilter==='all'||txt.includes(woFilter.toLowerCase())):true;
        const mi=t==='ib'?(invFilter==='all'||(invFilter==='low'&&txt.includes('low stock'))||(invFilter==='ok'&&txt.includes('in stock'))):true;
        r.style.display=ms&&mf&&mi?'':'none';
    });
}

function confirmDelete(title, message, onConfirm) {
    const ov = document.createElement('div'); ov.className = 'modal-overlay';
    ov.innerHTML = `<div class="modal" style="max-width:400px;text-align:center;"><div class="modal-title">${title}</div><p style="color:var(--text2);margin-bottom:20px;">${message}</p>
        <div class="form-actions" style="justify-content:center;"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-danger" style="background:var(--red);color:#fff;" id="confirmBtn">Delete</button></div></div>`;
    document.body.appendChild(ov);
    document.getElementById('confirmBtn').addEventListener('click',()=>{ov.remove();onConfirm();});
    ov.addEventListener('click',e=>{if(e.target===ov)ov.remove();});
}

function showToast(message, type) {
    type = type || 'info';
    const icons = {success:'fa-check-circle',error:'fa-exclamation-circle',info:'fa-info-circle'};
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.innerHTML = `<i class="fas ${icons[type]||'fa-info-circle'}"></i> ${message}`;
    document.getElementById('toastContainer').appendChild(t);
    setTimeout(()=>{t.style.animation='slideOut 0.3s ease forwards';setTimeout(()=>t.remove(),300);},3500);
}

function logout() { localStorage.removeItem('token'); localStorage.removeItem('user'); window.location.href = '/api/auth/login-page/'; }

// Init
function loadUserInfo() {
    try {
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        if (userData.username) {
            document.getElementById('userName').textContent = userData.username;
            document.getElementById('userAvatar').textContent = userData.username[0].toUpperCase();
        }
        if (userData.role && userData.garage_name) {
            document.getElementById('garageName').textContent = userData.garage_name + ' • ' + userData.role;
        } else if (userData.garage_name) {
            document.getElementById('garageName').textContent = userData.garage_name;
        } else if (userData.role) {
            document.getElementById('garageName').textContent = userData.role;
        }
    } catch(e) {
        console.log('User info load error:', e);
    }
}

// Run immediately and also after dashboard loads
loadUserInfo();
setTimeout(loadUserInfo, 1000);
setTimeout(loadUserInfo, 3000);

if (window.innerWidth <= 768) document.getElementById('hamburgerBtn').style.display = 'flex';
window.addEventListener('resize', () => {
    if (window.innerWidth <= 768) document.getElementById('hamburgerBtn').style.display = 'flex';
    else { document.getElementById('hamburgerBtn').style.display = 'none'; closeSidebar(); }
});

loadSection('dashboard');
