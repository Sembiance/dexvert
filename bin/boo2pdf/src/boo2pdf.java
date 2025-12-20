import java.io.*;

public class boo2pdf {

	public static void main(String[] args) {

		//String runDir = System.getProperty("user.dir") + "/../sys/";
		//String runDir = "/home/kev009/Downloads/sys/";

		String runDir = args[1];

		// Check for UNICODE table?
		File var6;
		var6 = new File(runDir + "libhlcwam.so");
		if (!var6.exists()) {
			System.out.println("\nERROR: Unable to open runtime library "
					+ var6);
			System.exit(1);
		}

		File unicodePage = new File(runDir + "EJRW850.TAB");
		if (!unicodePage.exists()) {
			System.out.println("\nERROR: Unable to open UNICODE Page, please make sure it is in the package.");
			System.exit(1);
		}

		System.out.println("Lib path: " + System.getenv("LD_LIBRARY_PATH"));

		Runtime.getRuntime().load(runDir + "libhlcwam.so");
		Runtime.getRuntime().load(runDir + "libhlctable.so");

		System.out.println("Starting...");
		System.out.println("runDir: " + runDir);

		//String rootName = args[3];

		// Open an HTML file handle for outputting body
		try {
			FileWriter fh = new FileWriter(args[3] + ".html");

			String[] args2 = {args[0],runDir};
			hlcBFrame frame = new hlcBFrame(args2);
			frame.setSize(800, 600);
			frame.setVisible(true);
			frame.openBook(args[2]);

			String html = "";
			fh.write("<html>\n<head>\n<title>" + frame.hlcJBook.jbGetjTitle()
					+ "</title>\n</head>\n\n<body>"); // Basic html header
			fh.write("<h1>" + frame.hlcJBook.jbGetjTitle() + "</h1>\n");
			fh.write("<b> Author: " + frame.hlcJBook.jbGetjAuthor()
					+ "</b><br>\n"); // Book Author
			fh.write("<b>Version: " + frame.hlcJBook.jbGetjVersion()
					+ "</b><br>\n"); // Book version number
			fh.write("<b>Document Number: " + frame.hlcJBook.jbGetjDocnum()
					+ "</b><br>\n"); // IBM Document number
			fh.write("<b>Build Date: " + frame.hlcJBook.jbGetjBuildDate()
					+ "</b><br>\n"); // Date book was assembled
			fh.write("<b>Copyright Date: " + frame.hlcJBook.jbGetjCopyright()
					+ "</b><br>\n"); // Copyright date
			fh.write("<br><i>Processed by <a href=\"http://www.kev009.com/wp/boo2pdf\">boo2pdf</a> (http://www.kev009.com/wp/boo2pdf)</i><br><br><hr><br><br>\n\n");

			int i = 1;
			while (frame.hlcJBook.topicExists(i)) {
				// System.out.println("Page: " + i);
				try {
					frame.hlcJBook.setTopic(i, true, false);
					// frame.displayTopic(i, true, false);
					html = frame.hlcJBook.getTopicBody(i, true, false, false);
					fh.write(html);

					i++;
				} catch (Exception e) {
					System.out.println(e);
					break;
				}
			}

			fh.write("<br><br><hr><br><i>Processed by <a href=\"http://www.kev009.com/wp/boo2pdf\">boo2pdf</a> (http://www.kev009.com/wp/boo2pdf)</i><br><br><hr><br><br>\n\n");
			fh.write("\n</body>\n</html>\n");

			fh.close();
		} catch (IOException e) {
			System.out.println("IO Exception: " + e);
		}

		System.out.println("Exit.");

		System.exit(0);
	}

}
