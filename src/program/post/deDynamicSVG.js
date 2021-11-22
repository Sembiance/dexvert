import {Program} from "../../Program.js";
import {runUtil} from "xutil";

export class deDynamicSVG extends Program
{
	website       = "https://github.com/Sembiance/dexvert";
	gentooPackage = "app-text/xmlstarlet";
	unsafe        = true;
	exec          = async r =>
	{
		const outFilePath = await r.outFile("out.svg", {absolute : true});
		await Deno.copyFile(r.inFile({absolute : true}), outFilePath);

		// The <title> and <desc> tags often have 'dynamic' info like current date and time of file generation, let's delete this uselessness so tests run better and labeling can know it's seen the file before
		await runUtil.run("xmlstarlet", ["ed", "--inplace", "-N", "s=http://www.w3.org/2000/svg", "--delete", "/s:svg/s:*[local-name()='desc' or local-name()='title' or local-name()='metadata']", outFilePath]);

		// A top level 'id' attribute on <svg> serves no real purpose other than to change the hash of the file every time it's generate, so let's get rid of it
		await runUtil.run("xmlstarlet", ["ed", "--inplace", "-N", "s=http://www.w3.org/2000/svg", "--delete", "/s:svg/@id", outFilePath]);

		// This will take care of deleting any 'empty' elements that totalCADConverter often does
		await runUtil.run("svgo", ["--multipass", "--final-newline", outFilePath]);
	}
}
