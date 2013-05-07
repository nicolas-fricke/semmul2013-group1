import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;

import javax.imageio.ImageIO;

import net.semanticmetadata.lire.imageanalysis.mpeg7.EdgeHistogramImplementation;

/**
	* @author tino junge
	*/

public class EdgeHistograms {

	/**
	 * @param args
	 */

	public static void main(String[] args) {

		File pic_folder = new File("../sample-pictures/");
		File[] listOfFiles = pic_folder.listFiles();

		for (File file : listOfFiles) {
			String pic_name = file.getName().split(".jpg")[0];
			System.out.println(pic_name);
			File img = new File(file.getAbsolutePath());
			try {
				// Get EdgeHistogram with Lire Implementation
				BufferedImage buffered_img = ImageIO.read(img);
				EdgeHistogramImplementation eh = new EdgeHistogramImplementation(buffered_img);
				int[] bins = eh.setEdgeHistogram();
				for (int i=0; i<bins.length; i++){
					System.out.print(bins[i]+" ");
				}
				System.out.println(" ");
				// Get EdgeHistogram from mirflick 1m txt file
				InputStream    fis;
				BufferedReader br;
				String         line;
				double [] eh_1m = new double[150];

				fis = new FileInputStream("../../data/metadata/features_edgehistogram/10/"+pic_name+".txt");
				br = new BufferedReader(new InputStreamReader(fis, Charset.forName("UTF-8")));
				int count = 0;
				while ((line = br.readLine()) != null) {
					eh_1m[count] = Double.parseDouble(line);
					System.out.print(eh_1m[count] + " ");
					count++;
				}
				System.out.println(" ");

				// Done with the file
				br.close();
				br = null;
				fis = null;


				// Compare EdgeHistograms
				int sq_sum = 0;
				for(int i : bins) {
					sq_sum += i;
				}

				for(int i=0; i<bins.length;i++) {
					System.out.print(bins[i] / (float) sq_sum+ " ");
				}
				System.out.println(" ");

				for (int i=0;i<bins.length;i++) {
					double val = eh_1m[i] / bins[i] ;
					System.out.print(val + " ");
				}
				System.out.println(" ");

			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
}
