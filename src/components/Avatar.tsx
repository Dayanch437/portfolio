interface AvatarProps {
  imageUrl: string;
  altText: string;
}

export default function Avatar({ imageUrl, altText }: AvatarProps) {
  return (
    <div className="hero__intro">
      <img
        className="avatar"
        src={imageUrl}
        alt={altText}
      />
    </div>
  );
}
