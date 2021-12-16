/* eslint-disable no-unused-vars */
import {xu} from "xu";
import {runUtil, fileUtil} from "xutil";
import {path, delay} from "std";


///mnt/compendium/DevLab/dexvert/test/sample/document/latex/LATEX.BUG
//[]

const tmpDirPath = await fileUtil.genTempPath();
await Deno.mkdir(tmpDirPath);

const tmpOutDir = await fileUtil.genTempPath();
await Deno.mkdir(tmpOutDir);

const runOptions = {verbose : true, killChildren : true, timeout : xu.SECOND*5, env : {TEXINPUTS : "/mnt/compendium/DevLab/dexvert/texmf"}};
const r = await runUtil.run("latex2html", ["-tmp", tmpDirPath, "-noinfo", "-html_version", "3.2,unicode,frame,math", "-image_type", "png", "-dir", tmpOutDir, "/mnt/compendium/DevLab/dexvert/test/sample/document/latex/LATEX.BUG"], runOptions);
console.log(r);

await fileUtil.unlink(tmpDirPath, {recursive : true});
await fileUtil.unlink(tmpOutDir, {recursive : true});

