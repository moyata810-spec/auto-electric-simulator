from flask import Flask, render_template_string

app = Flask(__name__)

# ==========================================
# ገጽ 1፡ LIGHTING SYSTEM HTML CODE
# ==========================================
LIGHTING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>3D Auto Electric: Lighting System</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; padding: 0; overflow: hidden; background: #06070a; font-family: sans-serif; color: #fff; }
        #canvas3d { width: 100vw; height: 100vh; display: block; }
        
        .hud-top {
            position: absolute; top: 6px; left: 8px; right: 8px;
            background: rgba(12, 16, 26, 0.88); backdrop-filter: blur(8px);
            border: 1px solid #1e293b; border-radius: 8px; padding: 6px;
            display: flex; justify-content: space-between; align-items: center; z-index: 100;
        }
        .hud-top h2 { margin: 0; font-size: 13px; color: #00e5ff; }
        .nav-btn {
            background: #0284c7; color: white; text-decoration: none; padding: 5px 10px;
            font-size: 11px; font-weight: bold; border-radius: 6px; border: 1px solid #38bdf8;
        }

        .hud-bottom {
            position: absolute; bottom: 6px; left: 6px; right: 6px;
            background: rgba(12, 16, 26, 0.94); backdrop-filter: blur(12px);
            border: 1px solid #334155; border-radius: 12px; padding: 8px;
            z-index: 100; max-height: 45vh; overflow-y: auto; box-shadow: 0 -4px 20px rgba(0,0,0,0.6);
        }

        .btn-row { display: flex; gap: 4px; justify-content: center; flex-wrap: wrap; margin-bottom: 6px; }
        .btn { padding: 6px 9px; font-size: 10px; font-weight: bold; border-radius: 6px; border: none; cursor: pointer; }
        .btn-sw { background: #1e293b; color: #94a3b8; border: 1px solid #475569; }
        .btn-sw.on { background: #10b981; color: white; border-color: #10b981; }
        .btn-dim { background: #d97706; color: white; border: 1px solid #f59e0b; }
        .btn-dim.high { background: #06b6d4; color: black; border-color: #06b6d4; }
        .btn-flash { background: #1e293b; color: #00e5ff; border: 1px solid #00e5ff; }
        .btn-flash.active { background: #00e5ff; color: #000; }
        .btn-haz { background: #1e293b; color: #94a3b8; border: 1px solid #475569; }
        .btn-haz.on { background: #f59e0b; color: #000; border-color: #f59e0b; }
        .btn-demo { background: #8b5cf6; color: white; }
        .btn-reset { background: #ef4444; color: white; }

        .pin-inspector {
            background: #0f172a; border: 1px solid #00e5ff; border-radius: 6px;
            padding: 5px 8px; font-size: 11px; font-family: monospace; color: #38bdf8;
            margin-bottom: 6px; text-align: left; font-weight: bold;
        }

        .pin-section { margin-bottom: 4px; text-align: left; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
        .section-title { font-size: 9px; font-weight: bold; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px; }
        .pin-pill {
            display: inline-block; padding: 3px 6px; font-size: 9px; font-weight: bold;
            border-radius: 4px; margin: 1px; cursor: pointer; border: 1px solid #334155; font-family: monospace;
            background: #1e293b; color: #f8fafc;
        }
        .pin-pill:hover, .pin-pill.selected { border-color: #00e5ff; background: #0284c7; color: white; }

        .diag-text { font-family: monospace; font-size: 10px; color: #22d3ee; text-align: left; line-height: 1.4; margin-top: 4px; }
    </style>
</head>
<body>

    <div id="canvas3d"></div>

    <div class="hud-top">
        <h2>🚗 1. Lighting System (የመብራት ገጽ)</h2>
        <a href="/starter" class="nav-btn">⚙️ ወደ Starting System ሂድ ➜</a>
    </div>

    <div class="hud-bottom">
        <div class="btn-row">
            <button class="btn btn-sw" id="swHeadBtn" onclick="toggleSwitch('head')">💡 HEAD SW: OFF</button>
            <button class="btn btn-dim" id="dimmerBtn" onclick="toggleDimmer()">🎛️ BEAM: LOW (አጭር)</button>
            <button class="btn btn-flash" id="flashBtn" onmousedown="setFlash(true)" onmouseup="setFlash(false)" ontouchstart="setFlash(true)" ontouchend="setFlash(false)">⚡ FLASH (PAS)</button>
            <button class="btn btn-sw" id="swTailBtn" onclick="toggleSwitch('tail')">🚨 TAIL SW: OFF</button>
            <button class="btn btn-haz" id="swHazBtn" onclick="toggleSwitch('haz')">⚠️ HAZ SW: OFF</button>
            <button class="btn btn-demo" onclick="runAutoDemo()">🎬 Demo</button>
            <button class="btn btn-reset" onclick="resetCircuit()">🔄 Reset</button>
        </div>

        <div class="pin-inspector" id="activePinDisplay">
            📌 የተመረጠ ፒን፦ ምንም አልተመረጠም (ፒን ንካ)
        </div>

        <div class="pin-section">
            <div class="section-title">🔋 ባትሪ (Power Source)</div>
            <span class="pin-pill" style="border-left: 3px solid #ef4444" onclick="selectPinByName('bat_pos')">+12 (Battery +)</span>
            <span class="pin-pill" style="border-left: 3px solid #64748b" onclick="selectPinByName('bat_neg')">GND (Ground -)</span>
        </div>

        <div class="pin-section">
            <div class="section-title">🔲 Relays (ሪሌዮች)</div>
            <span style="font-size:9px; color:#aaa;">R1-Head:</span>
            <span class="pin-pill" onclick="selectPinByName('r1_30')">H30</span>
            <span class="pin-pill" onclick="selectPinByName('r1_87')">H87</span>
            <span class="pin-pill" onclick="selectPinByName('r1_86')">H86</span>
            <span class="pin-pill" onclick="selectPinByName('r1_85')">H85</span>
            <span style="font-size:9px; color:#aaa; margin-left:4px;">R2-Tail:</span>
            <span class="pin-pill" onclick="selectPinByName('r2_30')">T30</span>
            <span class="pin-pill" onclick="selectPinByName('r2_87')">T87</span>
            <span class="pin-pill" onclick="selectPinByName('r2_86')">T86</span>
            <span class="pin-pill" onclick="selectPinByName('r2_85')">T85</span>
        </div>

        <div class="pin-section">
            <div class="section-title">🎛️ 5-Pin Dimmer & Dash Indicator</div>
            <span class="pin-pill" onclick="selectPinByName('dm_in')">DIN (Power In)</span>
            <span class="pin-pill" onclick="selectPinByName('dm_low')">DML (Low Out)</span>
            <span class="pin-pill" onclick="selectPinByName('dm_high')">DMH (High Out)</span>
            <span class="pin-pill" onclick="selectPinByName('dm_ind')">IND (Indicator)</span>
            <span class="pin-pill" onclick="selectPinByName('dm_pas')">PAS (Flash In)</span>
            <span class="pin-pill" onclick="selectPinByName('id_pos')">ID+</span>
            <span class="pin-pill" onclick="selectPinByName('id_neg')">ID-</span>
        </div>

        <div class="pin-section">
            <div class="section-title">⚠️ Flasher & Switches</div>
            <span class="pin-pill" onclick="selectPinByName('fl_b')">FLB</span>
            <span class="pin-pill" onclick="selectPinByName('fl_l')">FLL</span>
            <span class="pin-pill" onclick="selectPinByName('fl_e')">FLE</span>
            <span class="pin-pill" onclick="selectPinByName('sh1')">SH1</span>
            <span class="pin-pill" onclick="selectPinByName('sh2')">SH2</span>
            <span class="pin-pill" onclick="selectPinByName('st1')">ST1</span>
            <span class="pin-pill" onclick="selectPinByName('st2')">ST2</span>
            <span class="pin-pill" onclick="selectPinByName('sz1')">SZ1</span>
            <span class="pin-pill" onclick="selectPinByName('sz2')">SZ2</span>
        </div>

        <div class="pin-section" style="border:none;">
            <div class="section-title">💡 Lights (መብራቶች)</div>
            <span class="pin-pill" onclick="selectPinByName('ll_pos')">LL+</span>
            <span class="pin-pill" onclick="selectPinByName('lh_pos')">LH+</span>
            <span class="pin-pill" onclick="selectPinByName('hl_neg')">HL-</span>
            <span class="pin-pill" onclick="selectPinByName('rl_pos')">RL+</span>
            <span class="pin-pill" onclick="selectPinByName('rh_pos')">RH+</span>
            <span class="pin-pill" onclick="selectPinByName('hr_neg')">HR-</span>
            <span class="pin-pill" onclick="selectPinByName('tl_pos')">TL+</span>
            <span class="pin-pill" onclick="selectPinByName('tl_neg')">TL-</span>
            <span class="pin-pill" onclick="selectPinByName('tr_pos')">TR+</span>
            <span class="pin-pill" onclick="selectPinByName('tr_neg')">TR-</span>
            <span class="pin-pill" onclick="selectPinByName('zl_pos')">ZL+</span>
            <span class="pin-pill" onclick="selectPinByName('zl_neg')">ZL-</span>
            <span class="pin-pill" onclick="selectPinByName('zr_pos')">ZR+</span>
            <span class="pin-pill" onclick="selectPinByName('zr_neg')">ZR-</span>
        </div>

        <div class="diag-text" id="diagOutput">
            🔍 <strong>ምርመራ፦</strong> ሰርኪዩቱ ዝግጁ ነው። ሽቦዎችን ማገናኘት ጀምር!
        </div>
    </div>

    <script>
        const PIN_DESCRIPTIONS = {
            'bat_pos': '+12 ➜ የባትሪ ፖዘቲቭ', 'bat_neg': 'GND ➜ የባትሪ ኔጌቲቭ / ቻሲስ',
            'r1_30': 'H30 ➜ Head Relay Pwr In', 'r1_87': 'H87 ➜ Head Relay Pwr Out (ወደ DIN)',
            'r1_86': 'H86 ➜ Head Relay Signal', 'r1_85': 'H85 ➜ Head Relay Coil Ground',
            'r2_30': 'T30 ➜ Tail Relay Pwr In', 'r2_87': 'T87 ➜ Tail Relay Pwr Out',
            'r2_86': 'T86 ➜ Tail Relay Signal', 'r2_85': 'T85 ➜ Tail Relay Coil Ground',
            'dm_in': 'DIN ➜ 5-Pin Dimmer Power In', 'dm_low': 'DML ➜ Dimmer Low Out',
            'dm_high': 'DMH ➜ Dimmer High Out', 'dm_ind': 'IND ➜ High Beam Indicator Out',
            'dm_pas': 'PAS ➜ Passing/Flash In', 'id_pos': 'ID+ ➜ Dash Indicator (+)',
            'id_neg': 'ID- ➜ Dash Indicator (-)', 'fl_b': 'FLB ➜ Flasher Battery In',
            'fl_l': 'FLL ➜ Flasher Load Out', 'fl_e': 'FLE ➜ Flasher Earth/Ground',
            'sh1': 'SH1 ➜ Head SW In', 'sh2': 'SH2 ➜ Head SW Out',
            'st1': 'ST1 ➜ Tail SW In', 'st2': 'ST2 ➜ Tail SW Out',
            'sz1': 'SZ1 ➜ Haz SW In', 'sz2': 'SZ2 ➜ Haz SW Out',
            'll_pos': 'LL+ ➜ Head L-Low', 'lh_pos': 'LH+ ➜ Head L-High', 'hl_neg': 'HL- ➜ Head L-GND',
            'rl_pos': 'RL+ ➜ Head R-Low', 'rh_pos': 'RH+ ➜ Head R-High', 'hr_neg': 'HR- ➜ Head R-GND',
            'tl_pos': 'TL+ ➜ Tail L+', 'tl_neg': 'TL- ➜ Tail L-',
            'tr_pos': 'TR+ ➜ Tail R+', 'tr_neg': 'TR- ➜ Tail R-',
            'zl_pos': 'ZL+ ➜ Haz L+', 'zl_neg': 'ZL- ➜ Haz L-',
            'zr_pos': 'ZR+ ➜ Haz R+', 'zr_neg': 'ZR- ➜ Haz R-'
        };

        const container = document.getElementById('canvas3d');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x06070a);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(0, 14, 18);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2.1;

        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.85);
        dirLight.position.set(5, 15, 8);
        scene.add(dirLight);

        const bench = new THREE.Mesh(
            new THREE.BoxGeometry(16, 0.4, 13),
            new THREE.MeshStandardMaterial({ color: 0x11131a, roughness: 0.85 })
        );
        bench.position.y = -0.2;
        scene.add(bench);

        const clickablePins = [];
        const pinsMap = {};

        function createPin(name, x, y, z, pinColor) {
            const pinGeo = new THREE.SphereGeometry(0.2, 16, 16);
            const pin = new THREE.Mesh(pinGeo, new THREE.MeshStandardMaterial({ color: pinColor }));
            pin.position.set(x, y, z);
            pin.userData = { name: name, origColor: pinColor };
            scene.add(pin);
            clickablePins.push(pin);
            pinsMap[name] = pin;
            return pin;
        }

        const bat = new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.5, 1.5), new THREE.MeshStandardMaterial({ color: 0x111 }));
        bat.position.set(-6, 0.75, 4.5);
        scene.add(bat);
        createPin('bat_pos', -6.5, 1.6, 4.5, 0xef4444);
        createPin('bat_neg', -5.5, 1.6, 4.5, 0x111111);

        function create3DRelay(x, z, prefix, colorCode) {
            const base = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.25, 1.8), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
            base.position.set(x, 0.12, z);
            scene.add(base);

            const cCase = new THREE.Mesh(
                new THREE.BoxGeometry(1.6, 1.4, 1.6),
                new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.32, transmission: 0.9 })
            );
            cCase.position.set(x, 0.85, z);
            scene.add(cCase);

            const coil = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.6, 16), new THREE.MeshStandardMaterial({ color: 0xb87333, metalness: 0.8 }));
            coil.position.set(x, 0.6, z);
            scene.add(coil);

            const arm = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.6, 0.3), new THREE.MeshStandardMaterial({ color: 0xdcdde1, metalness: 0.9 }));
            arm.position.set(x + 0.35, 0.7, z);
            scene.add(arm);

            createPin(prefix + '_30', x - 0.45, 0.25, z - 0.45, 0xf97316);
            createPin(prefix + '_87', x + 0.45, 0.25, z - 0.45, colorCode);
            createPin(prefix + '_86', x - 0.45, 0.25, z + 0.45, 0x38bdf8);
            createPin(prefix + '_85', x + 0.45, 0.25, z + 0.45, 0x111111);
            return arm;
        }

        const armRelay1 = create3DRelay(-3.0, 0.5, 'r1', 0xeab308);
        const armRelay2 = create3DRelay(1.2, 0.5, 'r2', 0xec4899);

        const dimMesh = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.4, 1.4), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
        dimMesh.position.set(-3.0, 0.2, -2.0);
        scene.add(dimMesh);

        createPin('dm_in', -3.8, 0.45, -2.3, 0xeab308);
        createPin('dm_low', -3.4, 0.45, -1.7, 0xfef08a);
        createPin('dm_high', -2.8, 0.45, -1.7, 0x06b6d4);
        createPin('dm_ind', -2.4, 0.45, -2.3, 0x38bdf8);
        createPin('dm_pas', -3.1, 0.45, -2.3, 0xef4444);

        const dashFrame = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.5, 0.8), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
        dashFrame.position.set(0.0, 0.25, -2.0);
        scene.add(dashFrame);

        const indBulb = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 16), new THREE.MeshBasicMaterial({ color: 0x032b43 }));
        indBulb.position.set(0.0, 0.55, -2.0);
        scene.add(indBulb);

        createPin('id_pos', -0.3, 0.45, -1.7, 0x38bdf8);
        createPin('id_neg', 0.3, 0.45, -1.7, 0x111111);

        function createSwitch(x, z, inName, outName) {
            const m = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.4, 1.0), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
            m.position.set(x, 0.2, z);
            scene.add(m);
            createPin(inName, x - 0.35, 0.45, z, 0xef4444);
            createPin(outName, x + 0.35, 0.45, z, 0x38bdf8);
        }
        createSwitch(-5.8, -2, 'sh1', 'sh2');
        createSwitch(1.6, -2, 'st1', 'st2');
        createSwitch(3.2, -2, 'sz1', 'sz2');

        const flashMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 1.1, 16), new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.5 }));
        flashMesh.position.set(5.5, 0.55, 0.5);
        scene.add(flashMesh);
        createPin('fl_b', 4.9, 0.25, 0.5, 0xef4444);
        createPin('fl_l', 5.5, 0.25, -0.1, 0xf59e0b);
        createPin('fl_e', 6.1, 0.25, 0.5, 0x111111);

        function createDualBeamHeadlight(x, z, lowName, highName, negName) {
            const m = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.5, 0.7, 24), new THREE.MeshStandardMaterial({ color: 0x333, metalness: 0.7 }));
            m.rotateX(Math.PI / 2);
            m.position.set(x, 0.65, z);
            scene.add(m);

            const lens = new THREE.Mesh(new THREE.CircleGeometry(0.65, 24), new THREE.MeshBasicMaterial({ color: 0x222 }));
            lens.position.set(x, 0.65, z - 0.36);
            lens.rotateY(Math.PI);
            scene.add(lens);

            const spot = new THREE.SpotLight(0xffea00, 0, 14, Math.PI / 4, 0.5, 1);
            spot.position.set(x, 0.65, z - 0.35);
            spot.target.position.set(x, -0.3, z - 6);
            scene.add(spot);
            scene.add(spot.target);

            createPin(lowName, x - 0.45, 0.25, z + 0.45, 0xfef08a);
            createPin(highName, x, 0.25, z + 0.45, 0x06b6d4);
            createPin(negName, x + 0.45, 0.25, z + 0.45, 0x111111);
            return { lens, spot };
        }
        const headL = createDualBeamHeadlight(-3.5, -4.8, 'll_pos', 'lh_pos', 'hl_neg');
        const headR = createDualBeamHeadlight(3.5, -4.8, 'rl_pos', 'rh_pos', 'hr_neg');

        function createTailLight(x, z, posName, negName) {
            const m = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.5, 0.5), new THREE.MeshStandardMaterial({ color: 0x222 }));
            m.position.set(x, 0.55, z);
            scene.add(m);

            const lens = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.4, 0.1), new THREE.MeshBasicMaterial({ color: 0x330000 }));
            lens.position.set(x, 0.55, z + 0.24);
            scene.add(lens);

            const pLight = new THREE.PointLight(0xff1122, 0, 4);
            pLight.position.set(x, 0.55, z + 0.4);
            scene.add(pLight);

            createPin(posName, x - 0.35, 0.25, z - 0.45, 0xec4899);
            createPin(negName, x + 0.35, 0.25, z - 0.45, 0x111111);
            return { lens, pLight };
        }
        const tailL = createTailLight(-3.5, 5.0, 'tl_pos', 'tl_neg');
        const tailR = createTailLight(3.5, 5.0, 'tr_pos', 'tr_neg');

        function createHazardLight(x, z, posName, negName) {
            const m = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.35, 16), new THREE.MeshStandardMaterial({ color: 0x222 }));
            m.position.set(x, 0.45, z);
            scene.add(m);

            const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.25, 16, 16), new THREE.MeshBasicMaterial({ color: 0x332200 }));
            bulb.position.set(x, 0.6, z);
            scene.add(bulb);

            const pLight = new THREE.PointLight(0xf59e0b, 0, 5);
            pLight.position.set(x, 0.8, z);
            scene.add(pLight);

            createPin(posName, x, 0.25, z + 0.45, 0xf59e0b);
            createPin(negName, x + (x > 0 ? 0.35 : -0.35), 0.25, z + 0.45, 0x111111);
            return { bulb, pLight };
        }
        const hazL = createHazardLight(-6.0, -4.5, 'zl_pos', 'zl_neg');
        const hazR = createHazardLight(6.0, -4.5, 'zr_pos', 'zr_neg');

        let wires = [];
        let selectedPin = null;
        let switches = { head: false, tail: false, haz: false, isHighBeam: false, isFlashing: false };
        let blinkTick = false;

        setInterval(() => {
            blinkTick = !blinkTick;
            evaluateCircuit();
        }, 450);

        function add3DWire(p1, p2, color = 0x00ffcc) {
            wires.push([p1, p2]);
            const pos1 = pinsMap[p1].position;
            const pos2 = pinsMap[p2].position;
            const midY = Math.max(pos1.y, pos2.y) + 1.2;
            const curve = new THREE.QuadraticBezierCurve3(
                pos1,
                new THREE.Vector3((pos1.x + pos2.x) / 2, midY, (pos1.z + pos2.z) / 2),
                pos2
            );
            const tube = new THREE.Mesh(
                new THREE.TubeGeometry(curve, 20, 0.05, 8, false),
                new THREE.MeshStandardMaterial({ color: color, roughness: 0.3 })
            );
            tube.userData = { isWire: true };
            scene.add(tube);
        }

        function clearAllWires() {
            wires = [];
            const toRemove = [];
            scene.traverse(obj => { if (obj.userData && obj.userData.isWire) toRemove.push(obj); });
            toRemove.forEach(w => scene.remove(w));
        }

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('pointerdown', (e) => {
            if (e.target.closest('.hud-top') || e.target.closest('.hud-bottom')) return;
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const hits = raycaster.intersectObjects(clickablePins);
            if (hits.length > 0) selectPinByName(hits[0].object.userData.name);
        });

        function selectPinByName(pinName) {
            const pin = pinsMap[pinName];
            const inspector = document.getElementById('activePinDisplay');
            const desc = PIN_DESCRIPTIONS[pinName] || pinName;

            if (!selectedPin) {
                selectedPin = pinName;
                pin.material.emissive.setHex(0x00ffcc);
                inspector.innerHTML = '📌 የተመረጠ፦ <span style="color:#00ffcc">' + desc + '</span> ➜ (ቀጣይ ፒን ምረጥ)';
            } else {
                if (selectedPin !== pinName) {
                    add3DWire(selectedPin, pinName);
                    inspector.innerHTML = '🔗 ተገናኘ፦ <span style="color:#10b981">' + (PIN_DESCRIPTIONS[selectedPin]||selectedPin) + ' ➜ ' + desc + '</span>';
                    evaluateCircuit();
                }
                pinsMap[selectedPin].material.emissive.setHex(0x000000);
                selectedPin = null;
            }
        }

        function resetCircuit() {
            clearAllWires();
            selectedPin = null;
            clickablePins.forEach(p => p.material.emissive.setHex(0x000000));
            switches = { head: false, tail: false, haz: false, isHighBeam: false, isFlashing: false };
            document.getElementById('activePinDisplay').innerHTML = '📌 የተመረጠ ፒን፦ ምንም አልተመረጠም (ፒን ንካ)';
            updateSwitchButtons();
            evaluateCircuit();
        }

        function toggleSwitch(type) {
            switches[type] = !switches[type];
            updateSwitchButtons();
            evaluateCircuit();
        }

        function toggleDimmer() {
            switches.isHighBeam = !switches.isHighBeam;
            updateSwitchButtons();
            evaluateCircuit();
        }

        function setFlash(state) {
            switches.isFlashing = state;
            const btn = document.getElementById('flashBtn');
            btn.className = state ? 'btn btn-flash active' : 'btn btn-flash';
            evaluateCircuit();
        }

        function updateSwitchButtons() {
            document.getElementById('swHeadBtn').className = switches.head ? 'btn btn-sw on' : 'btn btn-sw';
            document.getElementById('swHeadBtn').innerText = switches.head ? '💡 HEAD SW: ON' : '💡 HEAD SW: OFF';

            const dimBtn = document.getElementById('dimmerBtn');
            dimBtn.className = switches.isHighBeam ? 'btn btn-dim high' : 'btn btn-dim';
            dimBtn.innerText = switches.isHighBeam ? '🎛️ BEAM: HIGH (ረጅም)' : '🎛️ BEAM: LOW (አጭር)';

            document.getElementById('swTailBtn').className = switches.tail ? 'btn btn-sw on' : 'btn btn-sw';
            document.getElementById('swTailBtn').innerText = switches.tail ? '🚨 TAIL SW: ON' : '🚨 TAIL SW: OFF';

            document.getElementById('swHazBtn').className = switches.haz ? 'btn btn-haz on' : 'btn btn-haz';
            document.getElementById('swHazBtn').innerText = switches.haz ? '⚠️ HAZ SW: ON' : '⚠️ HAZ SW: OFF';
        }

        function checkPath(p1, p2, r1Closed, r2Closed) {
            let adj = {};
            wires.forEach(w => {
                adj[w[0]] = adj[w[0]] || []; adj[w[1]] = adj[w[1]] || [];
                adj[w[0]].push(w[1]); adj[w[1]].push(w[0]);
            });

            if (switches.head) {
                adj['sh1'] = adj['sh1'] || []; adj['sh2'] = adj['sh2'] || [];
                adj['sh1'].push('sh2'); adj['sh2'].push('sh1');
            }
            if (switches.tail) {
                adj['st1'] = adj['st1'] || []; adj['st2'] = adj['st2'] || [];
                adj['st1'].push('st2'); adj['st2'].push('st1');
            }
            if (switches.haz) {
                adj['sz1'] = adj['sz1'] || []; adj['sz2'] = adj['sz2'] || [];
                adj['sz1'].push('sz2'); adj['sz2'].push('sz1');
            }

            if (r1Closed) {
                adj['r1_30'] = adj['r1_30'] || []; adj['r1_87'] = adj['r1_87'] || [];
                adj['r1_30'].push('r1_87'); adj['r1_87'].push('r1_30');
            }
            if (r2Closed) {
                adj['r2_30'] = adj['r2_30'] || []; adj['r2_87'] = adj['r2_87'] || [];
                adj['r2_30'].push('r2_87'); adj['r2_87'].push('r2_30');
            }

            if (!switches.isHighBeam) {
                adj['dm_in'] = adj['dm_in'] || []; adj['dm_low'] = adj['dm_low'] || [];
                adj['dm_in'].push('dm_low'); adj['dm_low'].push('dm_in');
            } else {
                adj['dm_in'] = adj['dm_in'] || []; adj['dm_high'] = adj['dm_high'] || []; adj['dm_ind'] = adj['dm_ind'] || [];
                adj['dm_in'].push('dm_high'); adj['dm_high'].push('dm_in');
                adj['dm_in'].push('dm_ind'); adj['dm_ind'].push('dm_in');
            }

            if (switches.isFlashing) {
                adj['dm_pas'] = adj['dm_pas'] || []; adj['dm_high'] = adj['dm_high'] || []; adj['dm_ind'] = adj['dm_ind'] || [];
                adj['dm_pas'].push('dm_high'); adj['dm_high'].push('dm_pas');
                adj['dm_pas'].push('dm_ind'); adj['dm_ind'].push('dm_pas');
            }

            let visited = new Set();
            let queue = [p1];
            while (queue.length > 0) {
                let curr = queue.shift();
                if (curr === p2) return true;
                visited.add(curr);
                (adj[curr] || []).forEach(nbr => { if (!visited.has(nbr)) queue.push(nbr); });
            }
            return false;
        }

        function evaluateCircuit() {
            let diag = [];

            const r1Coil = checkPath('bat_pos', 'r1_86', false, false) && checkPath('bat_neg', 'r1_85', false, false);
            armRelay1.position.x = r1Coil ? -2.85 : -2.65;
            armRelay1.material.color.setHex(r1Coil ? 0x00ffcc : 0xdcdde1);

            const r2Coil = checkPath('bat_pos', 'r2_86', false, false) && checkPath('bat_neg', 'r2_85', false, false);
            armRelay2.position.x = r2Coil ? 1.35 : 1.55;
            armRelay2.material.color.setHex(r2Coil ? 0x00ffcc : 0xdcdde1);

            const gndHL = checkPath('bat_neg', 'hl_neg', r1Coil, r2Coil);
            const gndHR = checkPath('bat_neg', 'hr_neg', r1Coil, r2Coil);

            const lowPwrL = checkPath('bat_pos', 'll_pos', r1Coil, r2Coil);
            const lowPwrR = checkPath('bat_pos', 'rl_pos', r1Coil, r2Coil);
            const lowActive = !switches.isHighBeam && !switches.isFlashing && (lowPwrL || lowPwrR) && (gndHL || gndHR);

            const highPwrL = checkPath('bat_pos', 'lh_pos', r1Coil, r2Coil);
            const highPwrR = checkPath('bat_pos', 'rh_pos', r1Coil, r2Coil);
            const highActive = (switches.isHighBeam || switches.isFlashing) && (highPwrL || highPwrR) && (gndHL || gndHR);

            if (lowActive) {
                headL.spot.color.setHex(0xfef08a);
                headL.spot.intensity = (lowPwrL && gndHL) ? 2.8 : 0;
                headL.spot.target.position.set(-3.5, -0.4, -9);
                headL.lens.material.color.setHex((lowPwrL && gndHL) ? 0xfef08a : 0x222222);

                headR.spot.color.setHex(0xfef08a);
                headR.spot.intensity = (lowPwrR && gndHR) ? 2.8 : 0;
                headR.spot.target.position.set(3.5, -0.4, -9);
                headR.lens.material.color.setHex((lowPwrR && gndHR) ? 0xfef08a : 0x222222);

                diag.push('💡 5-PIN DIMMER ➜ LOW BEAM (አጭር ብርሃን) በርቷል!');
            } else if (highActive) {
                headL.spot.color.setHex(0x06b6d4);
                headL.spot.intensity = (highPwrL && gndHL) ? 5.5 : 0;
                headL.spot.target.position.set(-3.5, 0.4, -14);
                headL.lens.material.color.setHex((highPwrL && gndHL) ? 0x06b6d4 : 0x222222);

                headR.spot.color.setHex(0x06b6d4);
                headR.spot.intensity = (highPwrR && gndHR) ? 5.5 : 0;
                headR.spot.target.position.set(3.5, 0.4, -14);
                headR.lens.material.color.setHex((highPwrR && gndHR) ? 0x06b6d4 : 0x222222);

                if (switches.isFlashing) diag.push('⚡ 5-PIN DIMMER ➜ FLASH (PAS) ብርሃን እየፈነጠቀ ነው!');
                else diag.push('🔦 5-PIN DIMMER ➜ HIGH BEAM (ረጅም/ፋር) በርቷል!');
            } else {
                headL.spot.intensity = 0; headL.lens.material.color.setHex(0x222222);
                headR.spot.intensity = 0; headR.lens.material.color.setHex(0x222222);
            }

            const indOn = checkPath('bat_pos', 'id_pos', r1Coil, r2Coil) && checkPath('bat_neg', 'id_neg', r1Coil, r2Coil);
            indBulb.material.color.setHex(indOn ? 0x00e5ff : 0x032b43);
            if (indOn) diag.push('🔵 Dashboard ➜ ሰማያዊው የ High Beam አመልካች በርቷል!');

            const onTL = checkPath('bat_pos', 'tl_pos', r1Coil, r2Coil) && checkPath('bat_neg', 'tl_neg', r1Coil, r2Coil);
            const onTR = checkPath('bat_pos', 'tr_pos', r1Coil, r2Coil) && checkPath('bat_neg', 'tr_neg', r1Coil, r2Coil);
            tailL.lens.material.color.setHex(onTL ? 0xff1122 : 0x330000);
            tailL.pLight.intensity = onTL ? 2.5 : 0;
            tailR.lens.material.color.setHex(onTR ? 0xff1122 : 0x330000);
            tailR.pLight.intensity = onTR ? 2.5 : 0;
            if (onTL && onTR) diag.push('🚨 Relay 2 (Tail) ➜ የኋላ ቀይ መብራቶች በርተዋል');

            const flActive = checkPath('bat_pos', 'fl_b', r1Coil, r2Coil) && checkPath('bat_neg', 'fl_e', r1Coil, r2Coil);
            const hazActive = flActive && checkPath('fl_l', 'zl_pos', r1Coil, r2Coil) && checkPath('bat_neg', 'zl_neg', r1Coil, r2Coil);
            const hzFlash = hazActive && blinkTick;
            hazL.bulb.material.color.setHex(hzFlash ? 0xf59e0b : 0x332200);
            hazL.pLight.intensity = hzFlash ? 3 : 0;
            hazR.bulb.material.color.setHex(hzFlash ? 0xf59e0b : 0x332200);
            hazR.pLight.intensity = hzFlash ? 3 : 0;
            if (hazActive) diag.push('⚠️ Flasher ➜ የአደጋ መብራቶች ብልጭ ድርግም እያሉ ነው!');

            if (diag.length === 0) diag.push('ሽቦዎችን አገናኝ ወይም ማብሪያዎቹን አብራ');
            document.getElementById('diagOutput').innerHTML = '🔍 <strong>ምርመራ፦</strong><br>' + diag.join('<br>');
        }

        function runAutoDemo() {
            resetCircuit();
            let step = 0;
            const steps = [
                () => add3DWire('bat_pos', 'sh1', 0xef4444),
                () => add3DWire('sh2', 'r1_86', 0x38bdf8),
                () => add3DWire('r1_85', 'bat_neg', 0x111111),
                () => add3DWire('bat_pos', 'r1_30', 0xf97316),
                () => add3DWire('r1_87', 'dm_in', 0xeab308),
                () => add3DWire('dm_low', 'll_pos', 0xfef08a),
                () => add3DWire('ll_pos', 'rl_pos', 0xfef08a),
                () => add3DWire('dm_high', 'lh_pos', 0x06b6d4),
                () => add3DWire('lh_pos', 'rh_pos', 0x06b6d4),
                () => add3DWire('dm_ind', 'id_pos', 0x38bdf8),
                () => add3DWire('id_neg', 'bat_neg', 0x111111),
                () => add3DWire('bat_pos', 'dm_pas', 0xef4444),
                () => add3DWire('hl_neg', 'bat_neg', 0x111111),
                () => add3DWire('hr_neg', 'bat_neg', 0x111111),
                () => toggleSwitch('head'),
                () => add3DWire('bat_pos', 'st1', 0xef4444),
                () => add3DWire('st2', 'r2_86', 0x38bdf8),
                () => add3DWire('r2_85', 'bat_neg', 0x111111),
                () => add3DWire('bat_pos', 'r2_30', 0xf97316),
                () => add3DWire('r2_87', 'tl_pos', 0xec4899),
                () => add3DWire('tl_pos', 'tr_pos', 0xec4899),
                () => add3DWire('tl_neg', 'bat_neg', 0x111111),
                () => add3DWire('tr_neg', 'bat_neg', 0x111111),
                () => toggleSwitch('tail'),
                () => add3DWire('bat_pos', 'sz1', 0xef4444),
                () => add3DWire('sz2', 'fl_b', 0xf59e0b),
                () => add3DWire('fl_e', 'bat_neg', 0x111111),
                () => add3DWire('fl_l', 'zl_pos', 0xf59e0b),
                () => add3DWire('zl_pos', 'zr_pos', 0xf59e0b),
                () => add3DWire('zl_neg', 'bat_neg', 0x111111),
                () => add3DWire('zr_neg', 'bat_neg', 0x111111),
                () => toggleSwitch('haz')
            ];

            const interval = setInterval(() => {
                if (step < steps.length) {
                    steps[step]();
                    evaluateCircuit();
                    step++;
                } else clearInterval(interval);
            }, 550);
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

# ==========================================
# ገጽ 2፡ STARTING SYSTEM HTML CODE (አዲሱ ገጽ)
# ==========================================
STARTER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>3D Auto Electric: Starting System</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; padding: 0; overflow: hidden; background: #06070a; font-family: sans-serif; color: #fff; }
        #canvas3d { width: 100vw; height: 100vh; display: block; }
        
        .hud-top {
            position: absolute; top: 6px; left: 8px; right: 8px;
            background: rgba(12, 16, 26, 0.88); backdrop-filter: blur(8px);
            border: 1px solid #1e293b; border-radius: 8px; padding: 6px;
            display: flex; justify-content: space-between; align-items: center; z-index: 100;
        }
        .hud-top h2 { margin: 0; font-size: 13px; color: #f59e0b; }
        .nav-btn {
            background: #1e293b; color: #38bdf8; text-decoration: none; padding: 5px 10px;
            font-size: 11px; font-weight: bold; border-radius: 6px; border: 1px solid #38bdf8;
        }

        .hud-bottom {
            position: absolute; bottom: 6px; left: 6px; right: 6px;
            background: rgba(12, 16, 26, 0.94); backdrop-filter: blur(12px);
            border: 1px solid #334155; border-radius: 12px; padding: 8px;
            z-index: 100; max-height: 45vh; overflow-y: auto; box-shadow: 0 -4px 20px rgba(0,0,0,0.6);
        }

        .btn-row { display: flex; gap: 4px; justify-content: center; flex-wrap: wrap; margin-bottom: 6px; }
        .btn { padding: 6px 10px; font-size: 11px; font-weight: bold; border-radius: 6px; border: none; cursor: pointer; }
        .btn-key { background: #334155; color: white; border: 1px solid #64748b; }
        .btn-key.active { background: #10b981; border-color: #10b981; }
        .btn-start { background: #d97706; color: white; border: 1px solid #f59e0b; }
        .btn-start.cranking { background: #ef4444; color: white; animation: pulse 0.3s infinite; }
        .btn-demo { background: #8b5cf6; color: white; }
        .btn-reset { background: #475569; color: white; }

        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }

        .pin-inspector {
            background: #0f172a; border: 1px solid #f59e0b; border-radius: 6px;
            padding: 5px 8px; font-size: 11px; font-family: monospace; color: #fbbf24;
            margin-bottom: 6px; text-align: left; font-weight: bold;
        }

        .pin-section { margin-bottom: 4px; text-align: left; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
        .section-title { font-size: 9px; font-weight: bold; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px; }
        .pin-pill {
            display: inline-block; padding: 3px 6px; font-size: 9px; font-weight: bold;
            border-radius: 4px; margin: 1px; cursor: pointer; border: 1px solid #334155; font-family: monospace;
            background: #1e293b; color: #f8fafc;
        }
        .pin-pill:hover, .pin-pill.selected { border-color: #f59e0b; background: #d97706; color: white; }

        .diag-text { font-family: monospace; font-size: 10px; color: #fbbf24; text-align: left; line-height: 1.4; margin-top: 4px; }
    </style>
</head>
<body>

    <div id="canvas3d"></div>

    <div class="hud-top">
        <h2>⚙️ 2. Starting System (የስታርተር ገጽ)</h2>
        <a href="/" class="nav-btn">⬅ ወደ Lighting System ተመለስ</a>
    </div>

    <div class="hud-bottom">
        <div class="btn-row">
            <button class="btn btn-key" id="keyIgnBtn" onclick="toggleIgnition()">🔑 KEY: OFF</button>
            <button class="btn btn-start" id="keyStartBtn" onmousedown="crankStart(true)" onmouseup="crankStart(false)" ontouchstart="crankStart(true)" ontouchend="crankStart(false)">⚡ CRANK (START)</button>
            <button class="btn btn-demo" onclick="runStarterDemo()">🎬 Demo (አስተምር)</button>
            <button class="btn btn-reset" onclick="resetStarterCircuit()">🔄 Reset</button>
        </div>

        <div class="pin-inspector" id="activePinDisplay">
            📌 የተመረጠ ፒን፦ ምንም አልተመረጠም (ፒን ንካ)
        </div>

        <div class="pin-section">
            <div class="section-title">🔋 ባትሪ (Heavy Cranking Battery)</div>
            <span class="pin-pill" style="border-left: 3px solid #ef4444" onclick="selectPinByName('bat_pos')">+12 (Heavy B+)</span>
            <span class="pin-pill" style="border-left: 3px solid #64748b" onclick="selectPinByName('bat_neg')">GND (Ground -)</span>
        </div>

        <div class="pin-section">
            <div class="section-title">🔑 Ignition Switch (የቁልፍ ማብሪያ)</div>
            <span class="pin-pill" onclick="selectPinByName('ign_am1')">AM1 (Bat In)</span>
            <span class="pin-pill" onclick="selectPinByName('ign_acc')">ACC (Accessory)</span>
            <span class="pin-pill" onclick="selectPinByName('ign_on')">IGN (Ignition ON)</span>
            <span class="pin-pill" onclick="selectPinByName('ign_sta')">STA (Starter Out)</span>
        </div>

        <div class="pin-section">
            <div class="section-title">🔲 Starter Relay (4-Pin)</div>
            <span class="pin-pill" onclick="selectPinByName('sr_30')">S30 (Pwr In)</span>
            <span class="pin-pill" onclick="selectPinByName('sr_87')">S87 (Out to T50)</span>
            <span class="pin-pill" onclick="selectPinByName('sr_86')">S86 (From STA)</span>
            <span class="pin-pill" onclick="selectPinByName('sr_85')">S85 (Ground)</span>
        </div>

        <div class="pin-section" style="border:none;">
            <div class="section-title">⚙️ Starter Motor & Solenoid</div>
            <span class="pin-pill" style="border-left: 3px solid #ef4444" onclick="selectPinByName('mot_b30')">B30 (Heavy Terminal 30)</span>
            <span class="pin-pill" style="border-left: 3px solid #f59e0b" onclick="selectPinByName('mot_t50')">T50 (Solenoid Coil Terminal 50)</span>
            <span class="pin-pill" style="border-left: 3px solid #64748b" onclick="selectPinByName('mot_gnd')">GND (Starter Chassis Ground)</span>
        </div>

        <div class="diag-text" id="diagOutput">
            🔍 <strong>ምርመራ፦</strong> የስታርተር ሰርኪዩት ተዘጋጅቷል። ሽቦዎችን አገናኝ!
        </div>
    </div>

    <script>
        const PIN_DESCRIPTIONS = {
            'bat_pos': '+12 ➜ የባትሪ ዋና ፖዘቲቭ (Heavy 12V)',
            'bat_neg': 'GND ➜ የባትሪ ኔጌቲቭ / ቻሲስ',
            'ign_am1': 'AM1 ➜ የቁልፍ ማብሪያ ኃይል መግቢያ (ከባትሪ)',
            'ign_acc': 'ACC ➜ መለዋወጫ (Accessory Out)',
            'ign_on': 'IGN ➜ የኢንጅን ኤሌክትሪክ ማብሪያ (Ignition ON)',
            'ign_sta': 'STA ➜ ወደ ስታርተር ሪሌይ የሚሄድ የስታርት ሲግናል',
            'sr_30': 'S30 ➜ Starter Relay ኃይል መግቢያ',
            'sr_87': 'S87 ➜ Starter Relay መውጫ (ወደ T50 ይሄዳል)',
            'sr_86': 'S86 ➜ Starter Relay ሲግናል (ከ STA የሚመጣ)',
            'sr_85': 'S85 ➜ Starter Relay ኮይል ግራውንድ',
            'mot_b30': 'B30 ➜ ስታርተር ሶሌኖይድ Terminal 30 (ወፍራሙ ኬብል)',
            'mot_t50': 'T50 ➜ ስታርተር ሶሌኖይድ Terminal 50 (መግነጢሱ መቀስቀሻ)',
            'mot_gnd': 'GND ➜ የስታርተር ሞተር አካል/ቻሲስ ግራውንድ'
        };

        const container = document.getElementById('canvas3d');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x06070a);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(0, 12, 16);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2.1;

        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.85);
        dirLight.position.set(5, 15, 8);
        scene.add(dirLight);

        // 3D Bench
        const bench = new THREE.Mesh(
            new THREE.BoxGeometry(16, 0.4, 12),
            new THREE.MeshStandardMaterial({ color: 0x11131a, roughness: 0.85 })
        );
        bench.position.y = -0.2;
        scene.add(bench);

        const clickablePins = [];
        const pinsMap = {};

        function createPin(name, x, y, z, pinColor) {
            const pinGeo = new THREE.SphereGeometry(0.2, 16, 16);
            const pin = new THREE.Mesh(pinGeo, new THREE.MeshStandardMaterial({ color: pinColor }));
            pin.position.set(x, y, z);
            pin.userData = { name: name, origColor: pinColor };
            scene.add(pin);
            clickablePins.push(pin);
            pinsMap[name] = pin;
            return pin;
        }

        // 1. 🔋 Heavy Battery
        const batMesh = new THREE.Mesh(new THREE.BoxGeometry(2.5, 1.8, 1.8), new THREE.MeshStandardMaterial({ color: 0x111 }));
        batMesh.position.set(-6, 0.9, 3.5);
        scene.add(batMesh);
        createPin('bat_pos', -6.6, 1.8, 3.5, 0xef4444);
        createPin('bat_neg', -5.4, 1.8, 3.5, 0x111111);

        // 2. 🔑 Ignition Switch (4-Pin)
        const ignBox = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 0.6, 24), new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.6 }));
        ignBox.position.set(-5.5, 0.3, -1.5);
        scene.add(ignBox);

        createPin('ign_am1', -6.2, 0.6, -1.8, 0xef4444);
        createPin('ign_acc', -6.2, 0.6, -1.2, 0x38bdf8);
        createPin('ign_on', -4.8, 0.6, -1.8, 0x10b981);
        createPin('ign_sta', -4.8, 0.6, -1.2, 0xf59e0b);

        // 3. 🔲 Starter Relay (4-Pin)
        const sRelayBase = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.25, 1.8), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
        sRelayBase.position.set(-1.5, 0.12, -1.5);
        scene.add(sRelayBase);

        const sRelayCase = new THREE.Mesh(
            new THREE.BoxGeometry(1.6, 1.4, 1.6),
            new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.32, transmission: 0.9 })
        );
        sRelayCase.position.set(-1.5, 0.85, -1.5);
        scene.add(sRelayCase);

        const sRelayCoil = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.6, 16), new THREE.MeshStandardMaterial({ color: 0xb87333, metalness: 0.8 }));
        sRelayCoil.position.set(-1.5, 0.6, -1.5);
        scene.add(sRelayCoil);

        const sRelayArm = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.6, 0.3), new THREE.MeshStandardMaterial({ color: 0xdcdde1, metalness: 0.9 }));
        sRelayArm.position.set(-1.15, 0.7, -1.5);
        scene.add(sRelayArm);

        createPin('sr_30', -1.95, 0.25, -1.95, 0xf97316);
        createPin('sr_87', -1.05, 0.25, -1.95, 0xf59e0b);
        createPin('sr_86', -1.95, 0.25, -1.05, 0x38bdf8);
        createPin('sr_85', -1.05, 0.25, -1.05, 0x111111);

        // 4. ⚙️ Starter Motor + Solenoid + Flywheel
        // Flywheel (ትልቅ ጥርስ ያለው ዲስክ)
        const flyGeo = new THREE.CylinderGeometry(2.2, 2.2, 0.35, 36);
        flyGeo.rotateX(Math.PI / 2);
        const flyMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.7, roughness: 0.4 });
        const flywheel = new THREE.Mesh(flyGeo, flyMat);
        flywheel.position.set(4.5, 1.5, -0.5);
        scene.add(flywheel);

        // Starter Motor Body (ዋናው የዲሲ ሞተር አካል)
        const motGeo = new THREE.CylinderGeometry(0.85, 0.85, 2.4, 24);
        motGeo.rotateZ(Math.PI / 2);
        const motMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.6 });
        const starterBody = new THREE.Mesh(motGeo, motMat);
        starterBody.position.set(1.5, 1.0, 1.2);
        scene.add(starterBody);

        // Starter Solenoid (ከላይ የተቀመጠው መግነጢሳዊ ሶሌኖይድ)
        const solGeo = new THREE.CylinderGeometry(0.5, 0.5, 1.6, 20);
        solGeo.rotateZ(Math.PI / 2);
        const solMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.7 });
        const solenoid = new THREE.Mesh(solGeo, solMat);
        solenoid.position.set(1.5, 2.0, 1.2);
        scene.add(solenoid);

        // Pinion Gear (የስታርተሩ ተንቀሳቃሽ ጥርስ / Bendix)
        const pinGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.5, 16);
        pinGeo.rotateX(Math.PI / 2);
        const pinMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.8 });
        const pinion = new THREE.Mesh(pinGeo, pinMat);
        pinion.position.set(3.0, 1.0, 1.2);
        scene.add(pinion);

        // Starter Terminals (B30, T50, GND)
        createPin('mot_b30', 0.6, 2.2, 1.2, 0xef4444);
        createPin('mot_t50', 1.5, 2.6, 1.2, 0xf59e0b);
        createPin('mot_gnd', 1.5, 0.25, 2.3, 0x111111);

        // Starter Circuit Logic & Animation
        let wires = [];
        let selectedPin = null;
        let keyState = 'OFF'; // OFF, ON
        let isCranking = false;
        let isMotorSpinning = false;

        function add3DWire(p1, p2, color = 0x00ffcc) {
            wires.push([p1, p2]);
            const pos1 = pinsMap[p1].position;
            const pos2 = pinsMap[p2].position;
            const midY = Math.max(pos1.y, pos2.y) + 1.2;
            const curve = new THREE.QuadraticBezierCurve3(
                pos1,
                new THREE.Vector3((pos1.x + pos2.x) / 2, midY, (pos1.z + pos2.z) / 2),
                pos2
            );
            const tube = new THREE.Mesh(
                new THREE.TubeGeometry(curve, 20, 0.05, 8, false),
                new THREE.MeshStandardMaterial({ color: color, roughness: 0.3 })
            );
            tube.userData = { isWire: true };
            scene.add(tube);
        }

        function clearAllWires() {
            wires = [];
            const toRemove = [];
            scene.traverse(obj => { if (obj.userData && obj.userData.isWire) toRemove.push(obj); });
            toRemove.forEach(w => scene.remove(w));
        }

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('pointerdown', (e) => {
            if (e.target.closest('.hud-top') || e.target.closest('.hud-bottom')) return;
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const hits = raycaster.intersectObjects(clickablePins);
            if (hits.length > 0) selectPinByName(hits[0].object.userData.name);
        });

        function selectPinByName(pinName) {
            const pin = pinsMap[pinName];
            const inspector = document.getElementById('activePinDisplay');
            const desc = PIN_DESCRIPTIONS[pinName] || pinName;

            if (!selectedPin) {
                selectedPin = pinName;
                pin.material.emissive.setHex(0xf59e0b);
                inspector.innerHTML = '📌 የተመረጠ፦ <span style="color:#fbbf24">' + desc + '</span> ➜ (ቀጣይ ፒን ምረጥ)';
            } else {
                if (selectedPin !== pinName) {
                    add3DWire(selectedPin, pinName);
                    inspector.innerHTML = '🔗 ተገናኘ፦ <span style="color:#10b981">' + (PIN_DESCRIPTIONS[selectedPin]||selectedPin) + ' ➜ ' + desc + '</span>';
                    evaluateStarterCircuit();
                }
                pinsMap[selectedPin].material.emissive.setHex(0x000000);
                selectedPin = null;
            }
        }

        function resetStarterCircuit() {
            clearAllWires();
            selectedPin = null;
            clickablePins.forEach(p => p.material.emissive.setHex(0x000000));
            keyState = 'OFF';
            isCranking = false;
            document.getElementById('keyIgnBtn').className = 'btn btn-key';
            document.getElementById('keyIgnBtn').innerText = '🔑 KEY: OFF';
            document.getElementById('activePinDisplay').innerHTML = '📌 የተመረጠ ፒን፦ ምንም አልተመረጠም (ፒን ንካ)';
            evaluateStarterCircuit();
        }

        function toggleIgnition() {
            keyState = (keyState === 'OFF') ? 'ON' : 'OFF';
            const btn = document.getElementById('keyIgnBtn');
            btn.className = (keyState === 'ON') ? 'btn btn-key active' : 'btn btn-key';
            btn.innerText = (keyState === 'ON') ? '🔑 KEY: ON (Ignition)' : '🔑 KEY: OFF';
            evaluateStarterCircuit();
        }

        function crankStart(state) {
            isCranking = state;
            const btn = document.getElementById('keyStartBtn');
            btn.className = state ? 'btn btn-start cranking' : 'btn btn-start';
            evaluateStarterCircuit();
        }

        function checkPath(p1, p2, srClosed) {
            let adj = {};
            wires.forEach(w => {
                adj[w[0]] = adj[w[0]] || []; adj[w[1]] = adj[w[1]] || [];
                adj[w[0]].push(w[1]); adj[w[1]].push(w[0]);
            });

            // Ignition Switch Internal Logic
            if (keyState === 'ON' || isCranking) {
                adj['ign_am1'] = adj['ign_am1'] || []; adj['ign_on'] = adj['ign_on'] || [];
                adj['ign_am1'].push('ign_on'); adj['ign_on'].push('ign_am1');
            }
            if (isCranking) {
                adj['ign_am1'] = adj['ign_am1'] || []; adj['ign_sta'] = adj['ign_sta'] || [];
                adj['ign_am1'].push('ign_sta'); adj['ign_sta'].push('ign_am1');
            }

            // Starter Relay Internal Contact (S30 connects to S87)
            if (srClosed) {
                adj['sr_30'] = adj['sr_30'] || []; adj['sr_87'] = adj['sr_87'] || [];
                adj['sr_30'].push('sr_87'); adj['sr_87'].push('sr_30');
            }

            let visited = new Set();
            let queue = [p1];
            while (queue.length > 0) {
                let curr = queue.shift();
                if (curr === p2) return true;
                visited.add(curr);
                (adj[curr] || []).forEach(nbr => { if (!visited.has(nbr)) queue.push(nbr); });
            }
            return false;
        }

        function evaluateStarterCircuit() {
            let diag = [];

            // 1. Starter Relay Coil Check
            const srCoil = checkPath('bat_pos', 'sr_86', false) && checkPath('bat_neg', 'sr_85', false);
            sRelayArm.position.x = srCoil ? -1.35 : -1.15;
            sRelayArm.material.color.setHex(srCoil ? 0x00ffcc : 0xdcdde1);

            // 2. Starter Solenoid Terminal 50 Check (from Relay S87)
            const t50HasPwr = checkPath('bat_pos', 'mot_t50', srCoil);
            const starterGnd = checkPath('bat_neg', 'mot_gnd', srCoil);
            const heavyPwr30 = checkPath('bat_pos', 'mot_b30', srCoil);

            // Solenoid Pull-in
            const solenoidActive = t50HasPwr && starterGnd;

            if (solenoidActive) {
                // Pinion slides forward towards flywheel!
                pinion.position.set(4.0, 1.0, -0.1);
                diag.push('🧲 Solenoid: ተስቦ የስታርተሩን ጥርስ ወደ ፍላይዊሉ ገፍቶታል!');
            } else {
                pinion.position.set(3.0, 1.0, 1.2);
            }

            // Motor Cranking Check (Heavy B30 + Solenoid engaged)
            if (solenoidActive && heavyPwr30) {
                isMotorSpinning = true;
                diag.push('⚡ CRANKING! ስታርተር ሞተሩ ፍላይዊሉን በከፍተኛ ኃይል እያሽከረከረ ነው!');
            } else {
                isMotorSpinning = false;
                if (solenoidActive && !heavyPwr30) {
                    diag.push('⚠️ ጥርሱ ተገፍቷል ግን ከባትሪ ወፍራሙ B30 ኬብል ስላልተሰካ ሞተሩ አልሾረም (Click only!)');
                }
            }

            if (keyState === 'ON' && !isCranking) diag.push('🔑 ቁልፉ በርቷል (Ignition ON)');
            if (diag.length === 0) diag.push('ሽቦዎችን አገናኝ ወይም ቁልፉን ወደ START አዙር');

            document.getElementById('diagOutput').innerHTML = '🔍 <strong>ምርመራ፦</strong><br>' + diag.join('<br>');
        }

        // 🎬 Auto-Demo for Starting System
        function runStarterDemo() {
            resetStarterCircuit();
            let step = 0;
            const steps = [
                // 1. Heavy Battery Cable to Starter B30
                () => add3DWire('bat_pos', 'mot_b30', 0xef4444),
                // 2. Starter Ground
                () => add3DWire('mot_gnd', 'bat_neg', 0x111111),
                // 3. Ignition Switch Power (AM1)
                () => add3DWire('bat_pos', 'ign_am1', 0xef4444),
                // 4. Starter Relay Circuit
                () => add3DWire('ign_sta', 'sr_86', 0xf59e0b),
                () => add3DWire('sr_85', 'bat_neg', 0x111111),
                () => add3DWire('bat_pos', 'sr_30', 0xf97316),
                () => add3DWire('sr_87', 'mot_t50', 0xf59e0b),
                // 5. Turn Key ON
                () => toggleIgnition(),
                // 6. Crank Engine!
                () => crankStart(true)
            ];

            const interval = setInterval(() => {
                if (step < steps.length) {
                    steps[step]();
                    evaluateStarterCircuit();
                    step++;
                } else {
                    clearInterval(interval);
                    // 3 ሰከንድ ፈጅቶ ክራንክ ያቆማል
                    setTimeout(() => { crankStart(false); }, 3000);
                }
            }, 600);
        }

        function animate() {
            requestAnimationFrame(animate);
            // ስታርተር ሞተር ሲሽከረከር ፍላይዊሉ እና ጥርሱ ይሽከረከራሉ
            if (isMotorSpinning) {
                flywheel.rotation.z += 0.25;
                pinion.rotation.z += 0.5;
            }
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

# ==========================================
# የ FLASK መስመሮች (ROUTES)
# ==========================================
@app.route('/')
def lighting_page():
    return render_template_string(LIGHTING_HTML)

@app.route('/starter')
def starter_page():
    return render_template_string(STARTER_HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
