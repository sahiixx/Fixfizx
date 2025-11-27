import { Helmet } from 'react-helmet-async';

const SEOHead = ({ 
  title, 
  description, 
  keywords, 
  ogImage,
  canonicalUrl,
  structuredData 
}) => {
  const defaultTitle = "NOWHERE.AI - #1 AI Digital Marketing Agency in Dubai | UAE";
  const defaultDescription = "Transform your Dubai business with AI-powered digital marketing. 500+ successful projects in UAE. Expert web development, SEO, social media, AI automation. 24/7 support.";
  const defaultKeywords = "AI digital marketing Dubai, digital marketing agency UAE, web development Dubai, SEO Dubai, social media marketing UAE, AI automation Dubai";
  const siteUrl = "https://nowhere.ai";
  
  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{title || defaultTitle}</title>
      <meta name="title" content={title || defaultTitle} />
      <meta name="description" content={description || defaultDescription} />
      <meta name="keywords" content={keywords || defaultKeywords} />
      
      {/* Open Graph / Facebook */}
      <meta property="og:type" content="website" />
      <meta property="og:url" content={canonicalUrl || siteUrl} />
      <meta property="og:title" content={title || defaultTitle} />
      <meta property="og:description" content={description || defaultDescription} />
      {ogImage && <meta property="og:image" content={ogImage} />}
      
      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={canonicalUrl || siteUrl} />
      <meta property="twitter:title" content={title || defaultTitle} />
      <meta property="twitter:description" content={description || defaultDescription} />
      {ogImage && <meta property="twitter:image" content={ogImage} />}
      
      {/* Canonical URL */}
      {canonicalUrl && <link rel="canonical" href={canonicalUrl} />}
      
      {/* Structured Data */}
      {structuredData && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
    </Helmet>
  );
};

export default SEOHead;
