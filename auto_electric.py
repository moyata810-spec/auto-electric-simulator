from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>3D Auto Electric: Low & High Fixed</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; padding: 0; overflow: hidden; background: #06070a; font-family: sans-serif; color: #fff; }
        #canvas3d { width: 100vw; height: 100vh; display: block; }
        
        .hud-top {
            position: absolute; top: 6px; left: 8px; right: 8px;
            background: rgba(12, 16, 26, 0.85); backdrop-filter: blur(8px);
            border: 1px solid #1e293b; border-radius: 8px; padding: 6px;
            text-align: center; z-index: 100;
        }
        .hud-top h2 { margin: 0; font-size: 13px; color: #00e5ff; }

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
        <h2>🚗 Dual Beam Headlights Fixed (Low & High)</h2>
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
            <span class="pin-pill" onclick="selectPinByName('ll_pos')">LL+ (Head L-Low)</span>
            <span class="pin-pill" onclick="selectPinByName('lh_pos')">LH+ (Head L-High)</span>
            <span class="pin-pill" onclick="selectPinByName('hl_neg')">HL- (Head L-GND)</span>
            <span class="pin-pill" onclick="selectPinByName('rl_pos')">RL+ (Head R-Low)</span>
            <span class="pin-pill" onclick="selectPinByName('rh_pos')">RH+ (Head R-High)</span>
            <span class="pin-pill" onclick="selectPinByName('hr_neg')">HR- (Head R-GND)</span>
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
            'bat_pos': '+12 ➜ የባትሪ ፖዘቲቭ (12V Main Feed)',
            'bat_neg': 'GND ➜ የባትሪ ኔጌቲቭ / ቻሲስ (Ground)',
            'r1_30': 'H30 ➜ Relay 1 ዋና የኃይል መግቢያ (Head Pwr In)',
            'r1_87': 'H87 ➜ Relay 1 ዋና የኃይል መውጫ (ወደ DIN ይሄዳል)',
            'r1_86': 'H86 ➜ Relay 1 ሲግናል ኮይል (ከ Head SW የሚመጣ)',
            'r1_85': 'H85 ➜ Relay 1 ኮይል ግራውንድ (ወደ GND ይሰካል)',
            'r2_30': 'T30 ➜ Relay 2 ዋና የኃይል መግቢያ (Tail Pwr In)',
            'r2_87': 'T87 ➜ Relay 2 ዋና የኃይል መውጫ (ወደ ኋላ መብራት)',
            'r2_86': 'T86 ➜ Relay 2 ሲግናል ኮይል (ከ Tail SW የሚመጣ)',
            'r2_85': 'T85 ➜ Relay 2 ኮይል ግራውንድ (ወደ GND ይሰካል)',
            'dm_in': 'DIN ➜ 5-Pin Dimmer ኃይል መግቢያ (ከ H87 የሚገባ)',
            'dm_low': 'DML ➜ Dimmer አጭር መብራት መውጫ (ወደ LL+ & RL+)',
            'dm_high': 'DMH ➜ Dimmer ረጅም መብራት መውጫ (ወደ LH+ & RH+)',
            'dm_ind': 'IND ➜ High Beam አመልካች መውጫ (ወደ ID+ ይሰካል)',
            'dm_pas': 'PAS ➜ Passing/Flash መግቢያ (ከባትሪ +12V ለፍላሽ)',
            'id_pos': 'ID+ ➜ Dashboard ሰማያዊ አምፑል (+)',
            'id_neg': 'ID- ➜ Dashboard ሰማያዊ አምፑል (- Ground)',
            'fl_b': 'FLB ➜ Flasher Battery In (+12V)',
            'fl_l': 'FLL ➜ Flasher Load Out (ወደ አደጋ መብራቶች)',
            'fl_e': 'FLE ➜ Flasher Earth (Ground -)',
            'sh1': 'SH1 ➜ Headlight Switch In',
            'sh2': 'SH2 ➜ Headlight Switch Out',
            'st1': 'ST1 ➜ Tail Light Switch In',
            'st2': 'ST2 ➜ Tail Light Switch Out',
            'sz1': 'SZ1 ➜ Hazard Switch In',
            'sz2': 'SZ2 ➜ Hazard Switch Out',
            'll_pos': 'LL+ ➜ የግራ የፊት መብራት አጭር ብርሃን (+)',
            'lh_pos': 'LH+ ➜ የግራ የፊት መብራት ረጅም ብርሃን (+)',
            'hl_neg': 'HL- ➜ የግራ የፊት መብራት Ground (-)',
            'rl_pos': 'RL+ ➜ የቀኝ የፊት መብራት አጭር ብርሃን (+)',
            'rh_pos': 'RH+ ➜ የቀኝ የፊት መብራት ረጅም ብርሃን (+)',
            'hr_neg': 'HR- ➜ የቀኝ የፊት መብራት Ground (-)',
            'tl_pos': 'TL+ ➜ የግራ የኋላ ቀይ መብራት (+)',
            'tl_neg': 'TL- ➜ የግራ የኋላ መብራት Ground (-)',
            'tr_pos': 'TR+ ➜ የቀኝ የኋላ ቀይ መብራት (+)',
            'tr_neg': 'TR- ➜ የቀኝ የኋላ መብራት Ground (-)',
            'zl_pos': 'ZL+ ➜ የግራ የአደጋ መብራት (+)',
            'zl_neg': 'ZL- ➜ የግራ የአደጋ መብራት Ground (-)',
            'zr_pos': 'ZR+ ➜ የቀኝ የአደጋ መብራት (+)',
            'zr_neg': 'ZR- ➜ የቀኝ የአደጋ መብራት Ground (-)'
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

        // 3D Bench
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

        // 1. 🔋 Battery
        const bat = new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.5, 1.5), new THREE.MeshStandardMaterial({ color: 0x111 }));
        bat.position.set(-6, 0.75, 4.5);
        scene.add(bat);
        createPin('bat_pos', -6.5, 1.6, 4.5, 0xef4444);
        createPin('bat_neg', -5.5, 1.6, 4.5, 0x111111);

        // 2. 🔲 Dual Relays
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

        const armRelay1 = create3DRelay(-3.0, 0.5, 'r1', 0xeab308); // Head Relay
        const armRelay2 = create3DRelay(1.2, 0.5, 'r2', 0xec4899);  // Tail Relay

        // 3. 🎛️ 5-Pin Dimmer Switch
        const dimMesh = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.4, 1.4), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
        dimMesh.position.set(-3.0, 0.2, -2.0);
        scene.add(dimMesh);

        createPin('dm_in', -3.8, 0.45, -2.3, 0xeab308);
        createPin('dm_low', -3.4, 0.45, -1.7, 0xfef08a);
        createPin('dm_high', -2.8, 0.45, -1.7, 0x06b6d4);
        createPin('dm_ind', -2.4, 0.45, -2.3, 0x38bdf8);
        createPin('dm_pas', -3.1, 0.45, -2.3, 0xef4444);

        // 4. 🔵 Dashboard High Beam Indicator
        const dashFrame = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.5, 0.8), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
        dashFrame.position.set(0.0, 0.25, -2.0);
        scene.add(dashFrame);

        const indBulb = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 16), new THREE.MeshBasicMaterial({ color: 0x032b43 }));
        indBulb.position.set(0.0, 0.55, -2.0);
        scene.add(indBulb);

        createPin('id_pos', -0.3, 0.45, -1.7, 0x38bdf8);
        createPin('id_neg', 0.3, 0.45, -1.7, 0x111111);

        // 5. 🔘 Switches (SH, ST, SZ)
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

        // 6. ⚠️ 3-Pin Flasher
        const flashMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 1.1, 16), new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.5 }));
        flashMesh.position.set(5.5, 0.55, 0.5);
        scene.add(flashMesh);
        createPin('fl_b', 4.9, 0.25, 0.5, 0xef4444);
        createPin('fl_l', 5.5, 0.25, -0.1, 0xf59e0b);
        createPin('fl_e', 6.1, 0.25, 0.5, 0x111111);

        // 7. 💡 Dual Headlights
        function createDualBeamHeadlight(x, z, lowName, highName, negName) {
            const m = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.5, 0.7, 24), new THREE.MeshStandardMaterial({ color: 0x333, metalness: 0.7 }));
            m.rotateX(Math.PI / 2);
            m.position.set(x, 0.65, z);
            scene.add(m);

            const lens = new THREE.Mesh(new THREE.CircleGeometry(0.65, 24), new THREE.MeshBasicMaterial({ color: 0x222 }));
            lens.position.set(x, 0.65, z - 0.36);
            lens.rotateY(Math.PI);
            scene.add(lens);

            // SpotLight
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

        // 8. 🚨 Tail Lights
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

        // 9. ⚠️ Hazard Lights
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

        // 10. 🔌 Wires & Fixed Circuit Engine
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

        // ሙሉ የኤሌክትሪክ ፍሰት መርማሪ (Electrical Adjacency Graph)
        function checkPath(p1, p2, r1Closed, r2Closed) {
            let adj = {};
            wires.forEach(w => {
                adj[w[0]] = adj[w[0]] || []; adj[w[1]] = adj[w[1]] || [];
                adj[w[0]].push(w[1]); adj[w[1]].push(w[0]);
            });

            // Switches
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

            // Relay 1 & Relay 2 Contacts (ዋናው ማስተካከያ እዚህ ነው!)
            if (r1Closed) {
                adj['r1_30'] = adj['r1_30'] || []; adj['r1_87'] = adj['r1_87'] || [];
                adj['r1_30'].push('r1_87'); adj['r1_87'].push('r1_30');
            }
            if (r2Closed) {
                adj['r2_30'] = adj['r2_30'] || []; adj['r2_87'] = adj['r2_87'] || [];
                adj['r2_30'].push('r2_87'); adj['r2_87'].push('r2_30');
            }

            // 5-Pin Dimmer Switch Routing
            if (!switches.isHighBeam) {
                // LOW BEAM: DIN connects strictly to DML
                adj['dm_in'] = adj['dm_in'] || []; adj['dm_low'] = adj['dm_low'] || [];
                adj['dm_in'].push('dm_low'); adj['dm_low'].push('dm_in');
            } else {
                // HIGH BEAM: DIN connects to DMH and IND
                adj['dm_in'] = adj['dm_in'] || []; adj['dm_high'] = adj['dm_high'] || []; adj['dm_ind'] = adj['dm_ind'] || [];
                adj['dm_in'].push('dm_high'); adj['dm_high'].push('dm_in');
                adj['dm_in'].push('dm_ind'); adj['dm_ind'].push('dm_in');
            }

            // Flash-To-Pass (PAS): Directly connects to DMH & IND
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

            // 1. Relay 1 (Head) Coil check
            const r1Coil = checkPath('bat_pos', 'r1_86', false, false) && checkPath('bat_neg', 'r1_85', false, false);
            armRelay1.position.x = r1Coil ? -2.85 : -2.65;
            armRelay1.material.color.setHex(r1Coil ? 0x00ffcc : 0xdcdde1);

            // 2. Relay 2 (Tail) Coil check
            const r2Coil = checkPath('bat_pos', 'r2_86', false, false) && checkPath('bat_neg', 'r2_85', false, false);
            armRelay2.position.x = r2Coil ? 1.35 : 1.55;
            armRelay2.material.color.setHex(r2Coil ? 0x00ffcc : 0xdcdde1);

            // 3. Headlights Check (Now passing r1Coil state!)
            const gndHL = checkPath('bat_neg', 'hl_neg', r1Coil, r2Coil);
            const gndHR = checkPath('bat_neg', 'hr_neg', r1Coil, r2Coil);

            // Low Beam Power Check
            const lowPwrL = checkPath('bat_pos', 'll_pos', r1Coil, r2Coil);
            const lowPwrR = checkPath('bat_pos', 'rl_pos', r1Coil, r2Coil);
            const lowActive = !switches.isHighBeam && !switches.isFlashing && (lowPwrL || lowPwrR) && (gndHL || gndHR);

            // High Beam Power Check
            const highPwrL = checkPath('bat_pos', 'lh_pos', r1Coil, r2Coil);
            const highPwrR = checkPath('bat_pos', 'rh_pos', r1Coil, r2Coil);
            const highActive = (switches.isHighBeam || switches.isFlashing) && (highPwrL || highPwrR) && (gndHL || gndHR);

            // 3D Visual Rendering for Low vs High
            if (lowActive) {
                // አጭር መብራት፦ ቢጫ ሞቅ ያለ ብርሃን ወደ ታች ያበራል
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
                // ረጅም መብራት፦ ደማቅ ሰማያዊ-ነጭ ረጅም ጨረር ወደ ፊት
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

            // Dashboard Blue Indicator (ID+, ID-)
            const indOn = checkPath('bat_pos', 'id_pos', r1Coil, r2Coil) && checkPath('bat_neg', 'id_neg', r1Coil, r2Coil);
            indBulb.material.color.setHex(indOn ? 0x00e5ff : 0x032b43);
            if (indOn) diag.push('🔵 Dashboard ➜ ሰማያዊው የ High Beam አመልካች በርቷል!');

            // 4. Tail Lights Check
            const onTL = checkPath('bat_pos', 'tl_pos', r1Coil, r2Coil) && checkPath('bat_neg', 'tl_neg', r1Coil, r2Coil);
            const onTR = checkPath('bat_pos', 'tr_pos', r1Coil, r2Coil) && checkPath('bat_neg', 'tr_neg', r1Coil, r2Coil);
            tailL.lens.material.color.setHex(onTL ? 0xff1122 : 0x330000);
            tailL.pLight.intensity = onTL ? 2.5 : 0;
            tailR.lens.material.color.setHex(onTR ? 0xff1122 : 0x330000);
            tailR.pLight.intensity = onTR ? 2.5 : 0;
            if (onTL && onTR) diag.push('🚨 Relay 2 (Tail) ➜ የኋላ ቀይ መብራቶች በርተዋል');

            // 5. Hazard & Flasher Check
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

        // 🎬 Auto-Demo (አጭር መብራትን በግልጽ አሳይቶ ወደ ረጅም ይቀይራል)
        function runAutoDemo() {
            resetCircuit();
            let step = 0;
            const steps = [
                // R1 (Head Relay)
                () => add3DWire('bat_pos', 'sh1', 0xef4444),
                () => add3DWire('sh2', 'r1_86', 0x38bdf8),
                () => add3DWire('r1_85', 'bat_neg', 0x111111),
                () => add3DWire('bat_pos', 'r1_30', 0xf97316),

                // 5-Pin Dimmer Wiring
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

                // 1. መጀመሪያ ስዊች ሲበራ አጭር መብራት (Low Beam) ይበራል!
                () => toggleSwitch('head'),

                // 2. Tail Lights
                () => add3DWire('bat_pos', 'st1', 0xef4444),
                () => add3DWire('st2', 'r2_86', 0x38bdf8),
                () => add3DWire('r2_85', 'bat_neg', 0x111111),
                () => add3DWire('bat_pos', 'r2_30', 0xf97316),
                () => add3DWire('r2_87', 'tl_pos', 0xec4899),
                () => add3DWire('tl_pos', 'tr_pos', 0xec4899),
                () => add3DWire('tl_neg', 'bat_neg', 0x111111),
                () => add3DWire('tr_neg', 'bat_neg', 0x111111),
                () => toggleSwitch('tail'),

                // 3. Hazard & Flasher
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

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
