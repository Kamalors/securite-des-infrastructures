// Crée le lab RAO dans EVE-NG PRO 7.2 (Freemium : 7 nœuds max) par l'API, depuis une session web ouverte.
// Usage : se connecter à https://localhost:8443 (tunnel SSH -L 8443:10.99.0.10:443), ouvrir la console
// du navigateur (F12) et coller ce script. Aucun mot de passe n'y figure : l'API utilise la session.
// Prérequis : image linux-debian13-routeur installée ; Cloud1-8 = pnet1-8 = vmbr2, vmbr10-16 (inventory/addressing.csv).
(async () => {
  const L = '/api/labs/RAO.unl';
  const send = (m, u, b) => fetch(u, {method: m, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(b)});
  await send('POST', '/api/labs', {path: '/', name: 'RAO', version: '1', author: 'RAO',
    description: 'Maquette RAO (7 noeuds reseau + hotes en LXC Proxmox)', body: ''});

  // Les identifiants de réseau suivent l'ordre de cette liste (1 à 14)
  const nets = [['Cloud1-gestion', 'pnet1'], ['Cloud2-dc1-dmz', 'pnet2'], ['Cloud3-dc1-app', 'pnet3'],
    ['Cloud4-dc1-data', 'pnet4'], ['Cloud5-dc1-adm', 'pnet5'], ['Cloud6-agfr-lan', 'pnet6'],
    ['Cloud7-inet-cli', 'pnet7'], ['Cloud8-agfr-invites', 'pnet8'], ['opA', 'bridge'], ['opB', 'bridge'],
    ['isp-ab', 'bridge'], ['dc2-lan', 'bridge'], ['hq-lan', 'bridge'], ['part-lan', 'bridge']];
  // Disposition : zones DC1 en haut à gauche, opérateurs au centre, sites à droite, gestion en bas
  const pos = [[1250, 830], [60, 60], [190, 60], [320, 60], [450, 60], [1500, 360], [980, 40], [1500, 470],
    [760, 250], [760, 560], [980, 400], [90, 620], [1500, 200], [1500, 600]];
  for (const [i, [name, type]] of nets.entries())
    await send('POST', L + '/networks', {count: 1, name, type, left: pos[i][0], top: pos[i][1], visibility: 1, postfix: 0});

  const tpl = (await (await fetch('/api/list/templates/linux')).json()).data.options;
  const defauts = Object.fromEntries(Object.entries(tpl).map(([k, v]) => [k, v.value]));
  // nom, icône, interfaces e0..eN -> id réseau ; e0 toujours sur la gestion (Cloud1)
  const nodes = [
    ['isp-a', 'Router.png', [1, 9, 7, 11], 760, 90],
    ['isp-b', 'Router.png', [1, 10, 11], 760, 700],
    ['fw-dc1', 'Firewall.png', [1, 9, 10, 2, 3, 4, 5], 330, 250],
    ['fw-dc2', 'Firewall.png', [1, 9, 10, 12], 330, 560],
    ['gw-hq', 'Firewall.png', [1, 9, 10, 13], 1250, 200],
    ['gw-agfr', 'Firewall.png', [1, 9, 10, 6, 8], 1250, 400],
    ['gw-part', 'Router.png', [1, 9, 14], 1250, 600],
  ];
  for (const [name, icon, links, left, top] of nodes) {
    const r = await (await send('POST', L + '/nodes', {...defauts, template: 'linux', type: 'qemu', count: 1, postfix: 0, name,
      image: 'linux-debian13-routeur', icon, cpu: 1, ram: 512, ethernet: links.length, console: 'telnet', delay: 0, left, top})).json();
    await send('PUT', L + '/nodes/' + r.data.id + '/interfaces', Object.fromEntries(links.map((n, k) => [k, n])));
  }
  console.log('Lab RAO créé ; démarrage : GET ' + L + '/nodes/{1..7}/start');
})();
