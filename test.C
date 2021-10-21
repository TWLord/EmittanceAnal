{
    TH1D h ("h", "",10,0,10);
    h.Sumw2();

    h.Fill(0.1, 2.);
    h.Fill(0.2, 4.);

    cout << "Original" << endl;
    cout << h.GetMean() << '\t' << h.GetMeanError() << endl;
    double stats1[4];
    h.GetStats(stats1);
    cout << stats1[0] << '\t'
         << stats1[1] << '\t' 
         << stats1[2] << '\t' 
         << stats1[3] << endl;

    cout << "After SetRange" << endl;
    h.GetXaxis()->SetRange(1,5);

    cout << h.GetMean() << '\t' << h.GetMeanError() << endl;
    double stats2[4];
    h.GetStats(stats2);
    cout << stats2[0] << '\t'
         << stats2[1] << '\t' 
         << stats2[2] << '\t' 
         << stats2[3] << endl;
}
