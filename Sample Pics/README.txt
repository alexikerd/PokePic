This is a collection of tests that I ran to make sure the autoencoder was working properly.

Original_Test and Model_Test was the autoencoder without any pooling, to make sure that the neural network was actually working (First time working with cnn on images)

The three 'Image Retrieval Test' pictures represent me finding the 5 closests encodings of pokemon using the network without pooling.
Because the reconstructed images were close to perfect, it allowed me to test if the KNN of encodings was working.

The two 'Real IR Test' pictures represent the smaller 50x50 image and the network with pooling.  The results for diglett are surprisingly similar with Dugtrio and Starmie showing up.

