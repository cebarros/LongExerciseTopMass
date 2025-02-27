#!/usr/bin/env python
import math, ROOT, json, optparse, os, sys, pprint
from ROOT import *

def myFitFunc(x=None,par=None):
    return par[0]*TMath.Gaus(x[0],par[1],par[2],kFALSE)

def gPeak(h=None,inDir=None,isData=None,lumi=None):

    # Set the stats off 
    gStyle.SetOptStat(0)
    gStyle.SetOptTitle(0)
    gStyle.SetTickLength(0.03)

    # Get the log(E) histogram 
    hFit = h.Clone()
    hFit.SetMarkerStyle(8)
    hFit.GetYaxis().SetTitleSize(0.062)
    hFit.GetYaxis().SetLabelSize(0.062)
    hFit.GetYaxis().SetTitleOffset(0.62)
    hFit.GetYaxis().SetTitle("1/E dN_{b jets}/dlog(E)")
    hFit.GetXaxis().SetLabelOffset(1)
    hFit.GetXaxis().SetTitle("log(E)")
    hFit.SetLineColor(kBlack)
    hFit.SetMarkerColor(kBlack)

    # Define the fit function and parameters
    ## Set limits
    minToFit = 3.6
    maxToFit = 4.8
    ## Set the function
    fitfunc = TF1("Gaussian fit", myFitFunc, minToFit, maxToFit, 3)
    ## Set normalization
    fitfunc.SetParameter(0, h.Integral());
    fitfunc.SetParLimits(0, 0.1*h.Integral(), 2.5*h.Integral());
    ## Set gaussian mean starting value and limits
    fitfunc.SetParameter(1, 4.2);
    fitfunc.SetParLimits(1, 4., 4.4);
    ## Set gaussian width starting value and limits
    fitfunc.SetParameter(2, 0.65);
    fitfunc.SetParLimits(2, 0.35, 0.95);
    ## Some cosmetics
    fitfunc.SetLineColor(kBlue)
    fitfunc.SetLineWidth(3)
    fitfunc.SetLineStyle(1)

    peak_xmin, peak_xmax = 65, 70

    #Histogram creation
    Pseudo_Exp = TH1F("Pseudo", "Pseudo", 100, peak_xmin, peak_xmax)
	  
    #Pseudoexperiments
    random3 = TRandom3()
    random3.SetSeed(1)
    num_experiments=1500 #change to 1500 later
    offset_p0, offset_p1 = 29.13, 0.5382
    for i in range(num_experiments):
         histoClone = h.Clone()
         for bin_n in range(histoClone.GetNbinsX()):
             x,y = histoClone.GetBinCenter(bin_n), histoClone.GetBinContent(bin_n)
             fluctuation = random3.PoissonD(y*math.exp(x))/math.exp(x)
             histoClone.SetBinContent(bin_n, y + fluctuation)
             #print(fluctuation)
	 histoClone.Fit("Gaussian fit","EMQ", "", minToFit, maxToFit)
         # Get Fit Parameters
    	 mean = fitfunc.GetParameter(1)
    	 meanErr = fitfunc.GetParError(1)
    	 sigma = fitfunc.GetParameter(2)
    	 sigmaErr = fitfunc.GetParError(2)
    	 chi2 = fitfunc.GetChisquare()
    	 NDF = fitfunc.GetNDF()
    	 chi2ndf = chi2/NDF
    	 # Calculate the uncalibrated Energy peak position and its uncertainty
    	 Ereco = math.exp(mean)
    	 Err = abs(Ereco*meanErr)
	 #print(i, '   ', Ereco)
         
         #Add calibration correction
         Ereco = (Ereco-offset_p0)/offset_p1
	 Pseudo_Exp.Fill(Ereco)
    
    fitfunc_pseudo = TF1("Gaussian Pseudo", myFitFunc, peak_xmin, peak_xmax, 3)
    ## Set normalization
    fitfunc_pseudo.SetParameter(0, 0.2*Pseudo_Exp.Integral());
    fitfunc_pseudo.SetParLimits(0, 0.01*Pseudo_Exp.Integral(), 0.5*Pseudo_Exp.Integral());
    ## Set gaussian mean starting value and limits
    fitfunc_pseudo.SetParameter(1, 67);
    fitfunc_pseudo.SetParLimits(1, 64, 70);
    ## Set gaussian width starting value and limits
    fitfunc_pseudo.SetParameter(2, 0.3);
    fitfunc_pseudo.SetParLimits(2, 0.01, 1.5);
    ## Some cosmetics
    fitfunc_pseudo.SetLineColor(kBlue)
    fitfunc_pseudo.SetLineWidth(3)
    fitfunc_pseudo.SetLineStyle(1)

    Pseudo_Exp.Fit("Gaussian Pseudo","EM", "", peak_xmin, peak_xmax)
    p_mean = fitfunc_pseudo.GetParameter(1)
    p_meanErr = fitfunc_pseudo.GetParError(1)
    p_sigma = fitfunc_pseudo.GetParameter(2)
    p_sigmaErr = fitfunc_pseudo.GetParError(2)
    p_chi2 = fitfunc_pseudo.GetChisquare()
    p_NDF = fitfunc_pseudo.GetNDF()
    p_chi2ndf = p_chi2/NDF
    # Calculate the uncalibrated Energy peak position and its uncertainty
    p_Ereco = math.exp(p_mean)
    p_Err = abs(p_Ereco*p_meanErr)
    
    pseudo_xmin, pseudo_xmax = 64.5, 71
    #Canvas
    c2 = TCanvas("Pseudo_Exp","Pseudo Experiment",800,800)
    c2.cd()
    Pseudo_Exp.GetXaxis().SetTitle("Energy Peak Position [GeV]")
    Pseudo_Exp.GetYaxis().SetTitle("Pseudo-experiments")
    Pseudo_Exp.Draw()
    Pseudo_Exp.GetXaxis().SetRangeUser(pseudo_xmin, pseudo_xmax)
    fitfunc_pseudo.Draw("Same")
    fitfunc_pseudo.GetXaxis().SetRangeUser(pseudo_xmin, pseudo_xmax)    

    p_caption1 = TLatex()
    p_caption1.SetTextSize(0.030)
    p_caption1.SetTextFont(42)
    p_caption1.SetNDC()
    p_caption1.DrawLatex(0.75,0.8,'Fit Results')
    p_caption1.DrawLatex(0.68,0.76,'#mu = %4.2f #pm %4.2f'%(p_mean,p_meanErr))
    p_caption1.DrawLatex(0.68,0.72,'#sigma = %4.2f #pm %4.2f'%(p_sigma,p_sigmaErr))
    p_caption1.DrawLatex(0.74,0.67,'#chi^{2}/ndf = %4.2f'%(p_chi2ndf))
   
    p_label1 = TLatex()
    p_label1.SetNDC()
    p_label1.SetTextFont(60)
    p_label1.SetTextSize(0.07)
    p_label1.SetTextAlign(31)
    p_label1.DrawLatex(0.32, 0.92, "CMS DAS")
    p_label2 = TLatex()
    p_label2.SetNDC()
    p_label2.SetTextFont(42)
    p_label2.SetTextSize(0.06)
    p_label2.SetTextAlign(11)
    p_label2.DrawLatex(0.33, 0.92, "#it{Simulation}")

    c2.Update()

    c2.SaveAs("pseudo.png")
	

    # Do the fit
    hFit.Fit("Gaussian fit","EM", "", minToFit, maxToFit) 
    # "E" stands for Minos, "M" for improving fit results
    # cf. ftp://root.cern.ch/root/doc/5FittingHistograms.pdf    

    # Get Fit Parameters
    mean = fitfunc.GetParameter(1)
    meanErr = fitfunc.GetParError(1)
    sigma = fitfunc.GetParameter(2)
    sigmaErr = fitfunc.GetParError(2)
    chi2 = fitfunc.GetChisquare()
    NDF = fitfunc.GetNDF()
    chi2ndf = chi2/NDF
    # Calculate the uncalibrated Energy peak position and its uncertainty
    Ereco = math.exp(mean)
    Err = abs(Ereco*meanErr)
    Ereco_corr = (Ereco-offset_p0)/offset_p1
    # Make a pull distribution    
    hPull = h.Clone("Pull")
    for ibin in range(1, hFit.GetNbinsX()+1):
        if hFit.GetBinCenter(ibin) > minToFit and hFit.GetBinCenter(ibin) <= maxToFit:
            binCont = hFit.GetBinContent(ibin)
            binErr = hFit.GetBinError(ibin)
            valIntegral = fitfunc.Eval(hFit.GetBinCenter(ibin))
            if binErr !=0:
              pull = (binCont-valIntegral)/binErr
              hPull.SetBinContent(ibin, pull)
              hPull.SetBinError(ibin, 1)
        else:      
            hPull.SetBinContent(ibin, 0.)
            hPull.SetBinError(ibin, 0.)
    hPull.SetMarkerStyle(8)
    hPull.GetYaxis().SetNdivisions(504)
    hPull.GetYaxis().SetTitleSize(0.140)
    hPull.GetYaxis().SetLabelSize(0.140)
    hPull.GetYaxis().SetTitleOffset(0.27)
    hPull.GetYaxis().SetTitle("#frac{Data-Fit}{Uncertainty}")
    hPull.GetXaxis().SetTitleSize(0.160)
    hPull.GetXaxis().SetLabelSize(0.150)
    hPull.GetXaxis().SetTitleOffset(0.8)
    hPull.GetXaxis().SetTitle("log(E)")
    hPull.SetLineColor(kBlack)
    hPull.SetMarkerColor(kBlack)

    # Plot the result
    ## Create a canvas with two pads for plotting your histograms
    c = TCanvas('c','c')
    c.cd()
    p1 = ROOT.TPad('p1','p1',0.,0.3,1.0,1.0)
    p1.SetBorderMode(0)
    p1.SetBorderSize(2)
    p1.SetTickx(1)
    p1.SetTicky(1)
    p1.SetTopMargin(0.13)
    p1.SetBottomMargin(0.02)
    p1.Draw()    
    p2 = ROOT.TPad('p2','p2',0.,0.,1.0,0.3)
    p2.SetGridy()
    p2.SetBorderMode(0)
    p2.SetBorderSize(2)
    p2.SetTickx(1)
    p2.SetTicky(1)
    p2.SetTopMargin(0.05)
    p2.SetBottomMargin(0.3)
    p2.Draw()
    ## Draw in the pad of the fit
    p1.cd()
    hFit.GetXaxis().SetRangeUser(minToFit,maxToFit)     
    hFit.Draw()
    ##Create some labels about the statistics
    caption1 = TLatex()
    caption1.SetTextSize(0.045)
    caption1.SetTextFont(42)
    caption1.SetNDC()
    caption1.DrawLatex(0.75,0.8,'Fit Results')
    caption1.DrawLatex(0.73,0.76,'#mu = %4.2f #pm %4.2f'%(mean,meanErr))
    caption1.DrawLatex(0.73,0.72,'#sigma = %4.2f #pm %4.2f'%(sigma,sigmaErr))
    caption1.DrawLatex(0.74,0.67,'#chi^{2}/ndf = %4.2f'%(chi2ndf))
    caption2 = TLatex()
    caption2.SetTextSize(0.05)
    caption2.SetTextFont(42)
    caption2.SetNDC()  
    caption2.DrawLatex(0.35,0.44,'Calibrated Measurement')
    caption2.DrawLatex(0.35,0.39,'<E_{b}> = (%4.2f #pm %4.2f) GeV'%(Ereco_corr,Err))
    ## CMS labels
    label1 = TLatex()
    label1.SetNDC()
    label1.SetTextFont(60)
    label1.SetTextSize(0.09)
    label1.SetTextAlign(31)
    label1.DrawLatex(0.19, 0.9, "CMS")
    label2 = TLatex()
    label2.SetNDC()
    label2.SetTextFont(42)
    label2.SetTextSize(0.0765)
    label2.SetTextAlign(11)
    if isData is True:
        label2.DrawLatex(0.2, 0.9, "#it{Preliminary}")
    else:
        label2.DrawLatex(0.2, 0.9, "#it{Simulation preliminary}")
    label3 = TLatex()
    label3.SetNDC()
    label3.SetTextFont(42)
    label3.SetTextSize(0.0765)
    label3.SetTextAlign(31)
    label3.DrawLatex(0.90, 0.9, "%d pb^{-1} (13 TeV)" % lumi)
    ## Edit the pad for the pull
    p2.cd()
    hPull.GetXaxis().SetRangeUser(minToFit,maxToFit)
    hPull.Draw("e")
    #a=input("")
    #save and delete
    sName = inDir+"/fit_";
    if isData is True:
        sName = sName+"Data";
    else: 
        sName = sName+"MC";
    c.SaveAs(sName+".pdf");
    c.SaveAs(sName+".png");
    del c
    fitfunc.IsA().Destructor(fitfunc)
    del caption1,caption2

    #all done here ;)
    return Ereco,Err

def main():

           usage = 'usage: %prog [options]'
           parser = optparse.OptionParser(usage)
           parser.add_option('-d', '--isData',  action = 'store_true',   dest='isData')
           parser.add_option('-i', '--inDir',   dest='inDir',   help='input directory',          default='nominal',    type='string')
           parser.add_option('-j', '--json',    dest='json',    help='json with list of files',  default="../analyzeNplot/data/samples_Run2015_25ns.json", type='string')
           parser.add_option('-l', '--lumi',    dest='lumi' ,   help='lumi to print out',        default=2444.,        type=float)
           (opt, args) = parser.parse_args()
           
           # Read list of MC samples
           if opt.isData is not True:
               samplesList=[]
               jsonFile = open(opt.json,'r')
               jsonList=json.load(jsonFile,encoding='utf-8').items()
               jsonFile.close()
               for tag,sample in jsonList: 
                   if not sample[3] in samplesList and not "Data" in sample[3]:
                       samplesList.append(sample[3])

           # Open the root file
           fiName = "../analyzeNplot/"+opt.inDir+"/plots/plotter.root"
           print "... processing", fiName
           if not os.path.isfile(fiName):
               print "Help, file doesn't exist"
               exit(-1)
           res = ROOT.TFile(fiName, "read")

           #Get the histogram 
           hName = "bjetenls/"   
           if opt.isData is True:
               hName = hName + "bjetenls"
           else:
               hName = hName + "bjetenls_" + samplesList[0]
           histo = res.Get(str(hName))
           histo.SetDirectory(0)
           if opt.isData is not True:
               for sampleInfo in samplesList:
                   if sampleInfo is not samplesList[0]: 
                       histo.Add(res.Get(str("bjetenls/bjetenls_"+sampleInfo)).Clone());

#           Pseudoexperiments
#           random3 = TRandom3()
#           random3.SetSeed(1)
#	   num_experiments=10 #change to 1500 later
#           for i in range(num_experiments):
#               histoClone = histo.Clone()
#               for bin_n in range(histoClone.GetNbinsX()):
#                   x,y = histoClone.GetBinCenter(bin_n), histoClone.GetBinContent(bin_n) 
#                   fluctuation = random3.PoissonD(y*math.exp(x))/math.exp(x)
#                   histoClone.SetBinContent(bin_n, y + fluctuation)   		
#                   print(fluctuation)

           # Create the output directory
           if not os.path.isdir(opt.inDir):
               os.mkdir(opt.inDir)

           # Calculate the energy peak position in the big MC sample
           Eb,DEb = gPeak(h=histo,inDir=opt.inDir,isData=opt.isData,lumi=opt.lumi)
           print "<E_{b}> = (%3.2f #pm %3.2f) GeV" % (Eb,DEb)
            
           res.Close()
               
if __name__ == "__main__":
    sys.exit(main())


