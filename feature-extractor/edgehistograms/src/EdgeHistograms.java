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


public class EdgeHistograms {
	
	public static void main(String[] args) {	
		
		File pic_folder = new File("../Pictures/");
		File[] listOfFiles = pic_folder.listFiles();
		
		for (File file : listOfFiles) {		
			String pic_name = file.getName().split(".jpg")[0];
			System.out.println("Picture ID: \t" + pic_name);
			File img = new File(file.getAbsolutePath());
			try {
				// Get EdgeHistogram with Lire Implementation
				BufferedImage buffered_img = ImageIO.read(img);
				EdgeHistogramImplementation eh = new EdgeHistogramImplementation(buffered_img);
				int[] bins = eh.setEdgeHistogram();
				System.out.print("Lire EH: \t");
				for (int i=0; i<bins.length; i++){
					System.out.print(bins[i]+"\t\t | ");
				}
				System.out.println(" ");
				// Get EdgeHistogram from mirflick 1m txt file
				InputStream    fis;
				BufferedReader br;
				String         line;
				double [] eh_1m = new double[150]; 

				fis = new FileInputStream("/Users/tinojunge/Downloads/features_edgehistogram/10/"+pic_name+".txt");
				br = new BufferedReader(new InputStreamReader(fis, Charset.forName("UTF-8")));
				int count = 0; 
				System.out.print("Mir1M EH: \t");
				while ((line = br.readLine()) != null) {
					eh_1m[count] = Double.parseDouble(line);
					System.out.print(eh_1m[count] + "\t | ");
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
				
				System.out.print("L1 Norm: \t");
				for(int i=0; i<bins.length;i++) {
					System.out.print(bins[i] / (float) sq_sum+ "\t | ");
				}
				System.out.println(" ");
				
				System.out.print("Distance : \t");
				for (int i=0;i<bins.length;i++) {
					double val = bins[i] - eh_1m[i] ;
					System.out.print(val + "\t | ");
				}
				System.out.println("\n");
				
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
