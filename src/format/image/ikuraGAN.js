import {Format} from "../../Format.js";

export class ikuraGAN extends Format
{
	name           = "Ikura GAN Animation Resource";
	ext            = [".gan"];
	forbidExtMatch = true;
	magic          = ["archive:Ikura.GanOpener"];
	converters     = ["GARbro[types:archive:Ikura.GanOpener]"];
}
