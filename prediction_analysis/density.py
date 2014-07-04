import matplotlib
matplotlib.use('PDF')
from ggplot import *

plot1=ggplot(diamonds, aes(x='price', color='cut')) +  geom_density()

from matplotlib.backends.backend_pdf import PdfPages

pp = PdfPages('foo.pdf')
pp.savefig(plot1)
pp.close()
