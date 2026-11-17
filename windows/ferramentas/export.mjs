import { loadProject, exportProject, gd_internal_logs } from "gdcore-tools";
const p = await loadProject(process.argv[2]);
console.log("loaded", p.getName(), p.getLayoutsCount());
exportProject(p, process.argv[3]);
console.log(gd_internal_logs.slice(-3000));
